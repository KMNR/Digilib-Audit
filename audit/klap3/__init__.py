import MySQLdb
import logging
from audit.klap3 import models
from unidecode import unidecode

logger = logging.getLogger(__name__)


def load(credentials):
    return KLAP3(*credentials)


class KLAP3(object):
    def __init__(self, username, password):
        self.db = MySQLdb.connect("localhost", username, password, "klap3")

    def create_view(self):
        logger.info('Creating table with album, artist, track count, '
                    'and library code data')
        cursor = self.db.cursor()
        cursor.execute('DROP TABLE IF EXISTS KLAP3AlbumSummary;')
        # TODO: GROUP_CONCAT(format SEPARATOR ',')
        cursor.execute(
            '''
                CREATE TABLE KLAP3AlbumSummary 
                       AS
                       SELECT Album.id AS id
                       ,      Album.name AS album
                       ,      Artist.name AS artist
                       ,      TrackCount.track_count AS track_count
                       ,      Genre.abbreviation AS libcode_genre
                       ,      Artist.lib_number AS libcode_artist
                       ,      Album.letter AS libcode_album
                       FROM   album Album
                       JOIN   artist Artist
                         ON   Album.artist_id=Artist.id
                       LEFT JOIN   (
                                SELECT Song.album_id AS album_id
                                ,      COUNT(*) AS track_count
                                FROM   song Song
                                GROUP  BY Song.album_id
                              ) TrackCount
                         ON   TrackCount.album_id=Album.id
                       JOIN   genre Genre
                         ON   Artist.genre_id=Genre.id
                ;
            '''
        )
        self.db.commit()
        cursor.close()

    def albums(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM KLAP3AlbumSummary')

        while True:
            t = cursor.fetchone()
            if t is None:
                break

            klap3_album = models.KLAP3Album(self, *t)
            yield klap3_album

        cursor.close()

    def find(self, album):
        logger.debug('Searching KLAP3 for {}'.format(album))
        
        cursor = self.db.cursor()

        # Find album by matching album title, artist name, and track count.
        cursor.execute(
            """
                SELECT id
                FROM   KLAP3AlbumSummary A
                WHERE  A.track_count=%s
                   AND LOWER(A.album)=%s
                   AND LOWER(A.artist)=%s
            """,
            (
                album.track_count,
                unidecode(album.title).lower(),
                unidecode(album.artist).lower(),
            )
        )

        matching_album_ids = [id for id, in cursor.fetchall()]
        cursor.close()

        logger.debug('{} KLAP3 albums found'.format(len(matching_album_ids)))

        if len(matching_album_ids) == 0:
            closest_matched_album_id = self.find_by_artist_and_track_count(album)
            if closest_matched_album_id is None:
                matching_album_ids = []
            else:
                matching_album_ids = [closest_matched_album_id]

        logger.debug('')
        return matching_album_ids

    def format_of(self, album_id):
        cursor = self.db.cursor()
        cursor.execute(
            '''
                SELECT short_name
                FROM   search_format
                WHERE  search_format.id
                   IN  (
                       SELECT format_id
                       FROM   album_format
                       WHERE  album_format.album_id=%s
                   )
            ''',
            (album_id,)
        )
        T = [t for t, in cursor.fetchmany()]
        T.sort()
        cursor.close()

        return ','.join(T)

    def find_by_artist_and_track_count(self, album):
        logger.debug('Finding albums by {} with {} songs'.format(
            album.artist, album.track_count
        ))

        cursor = self.db.cursor()

        # Grab the names and ids of albums performed by an artist
        #  with a given number of songs.

        cursor.execute(
            '''
                SELECT id
                ,      album
                FROM   KLAP3AlbumSummary
                WHERE  artist=%s
                  AND  track_count=%s
            ''',
            (
                album.artist,
                album.track_count
            )
        )

        # cursor.execute(
        #     '''
        #         SELECT album.id
        #         ,      album.name
        #         FROM   album
        #         WHERE  album.id IN (
        #             SELECT album_id
        #             FROM   song
        #             WHERE  song.album_id IN (
        #                 SELECT album.id
        #                 FROM   album
        #                 WHERE  album.artist_id IN (
        #                     SELECT artist.id
        #                     FROM   artist
        #                     WHERE  LOWER(artist.name)=%s
        #                 )
        #             )
        #             GROUP BY song.album_id
        #             HAVING COUNT(*)=%s
        #         )
        #     ''',
        #     (
        #         album.artist,
        #         album.track_count
        #     )
        # )

        matching_albums = cursor.fetchall()
        cursor.close()

        logger.debug('{} albums found'.format(len(matching_albums)))
        if 0==len(matching_albums):
            return None

        # Isolate the album that has the most matching words as that of
        #  the given album.

        strip_away_non_alphanums = lambda x: ''.join(c for c in x if
                                                     c.isalnum())
        strip_away_from_all_words = lambda x: [
            strip_away_non_alphanums(w)
            for w in x
            if strip_away_non_alphanums(w)
        ]
        set_of_proper_lowercase_words = lambda s: set(
            strip_away_from_all_words(unidecode(s).lower().split(' '))
        )

        words_of_given_album_title = set_of_proper_lowercase_words(album.title)

        logger.debug('Words in given album title: {}'.format(
            words_of_given_album_title))
        logger.debug('Found album words:')
        for album_id, album_title in matching_albums:
            logger.debug(set_of_proper_lowercase_words(album_title))
        logger.debug('-'*80)

        album_name_word_match_count = lambda album: len(
            words_of_given_album_title.intersection(
                set_of_proper_lowercase_words(album[1])
            )
        )

        most_closely_matched_album = max(
            matching_albums,
            key=album_name_word_match_count,
        )
        logger.debug('Album with closest match: {}'.format(
            most_closely_matched_album[1]))
        logger.debug('Compared to search album: {}'.format(
            album.title
        ))

        import time
        if album_name_word_match_count(most_closely_matched_album) == 0:
            logger.debug('No sufficient match')
            return None
        else:
            logger.debug('Sufficient match!')
            return most_closely_matched_album[0]
