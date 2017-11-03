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
        # Create a table consisting of data we'll be using. This will speed
        # up the execution of this script instead of performing a bunch of
        # select statements with lots of joins.
        logger.info('Creating table with album, artist, track count, '
                    'and library code data')
        cursor = self.db.cursor()
        cursor.execute('DROP TABLE IF EXISTS KLAP3AlbumSummary;')
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
                       ,      Format.mediums AS mediums
                       ,      Album.missing AS is_missing
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
                       JOIN   (
                                SELECT GROUP_CONCAT(Format.short_name
                                                    SEPARATOR ',') AS mediums
                                ,      AlbumFormat.album_id AS album_id
                                FROM   search_format Format
                                JOIN   album_format AlbumFormat
                                  ON   AlbumFormat.format_id=Format.id
                                GROUP  BY AlbumFormat.album_id
                                ORDER  BY Format.short_name
                              ) Format
                         ON   Album.id=Format.album_id
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
                WHERE  LOWER(A.album)=%s
                   AND LOWER(A.artist)=%s
            """,
            (
                unidecode(album.title).lower(),
                unidecode(album.artist).lower(),
            )
        )

        matching_album_ids = [id for id, in cursor.fetchall()]
        cursor.close()

        logger.debug('{} KLAP3 albums found'.format(len(matching_album_ids)))

        if not matching_album_ids:
            closest_matched_album_id = self.find_by_artist_and_track_count(album)
            if closest_matched_album_id is not None:
                matching_album_ids = [closest_matched_album_id]

        if not matching_album_ids:
            matching_album_name_and_track_count_id = self.find_by_matching_album_and_id(album)
            if matching_album_name_and_track_count_id is not None:
                matching_album_ids = [matching_album_name_and_track_count_id]

        logger.debug('')
        return matching_album_ids

    def find_by_matching_album_and_id(self, album):
        logger.debug('Finding albums by {} with {} songs'.format(
            album.title, album.track_count
        ))

        cursor = self.db.cursor()

        # Grab the names and ids of albums performed by an artist
        #  with a given number of songs.

        cursor.execute(
            '''
                SELECT id
                ,      artist
                FROM   KLAP3AlbumSummary
                WHERE  LOWER(album)=%s
                  AND  track_count=%s
            ''',
            (
                unidecode(album.title).lower(),
                album.track_count
            )
        )

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

        words_of_given_artist_name = set_of_proper_lowercase_words(album.artist)

        logger.debug('Words in given artist name: {}'.format(
            words_of_given_artist_name))
        logger.debug('Found artist name words:')
        for album_id, album_artist in matching_albums:
            logger.debug(set_of_proper_lowercase_words(album_artist))
        logger.debug('-'*80)

        artist_name_word_match_count = lambda album: len(
            words_of_given_artist_name.intersection(
                set_of_proper_lowercase_words(album[1])
            )
        )

        most_closely_matched_album = max(
            matching_albums,
            key=artist_name_word_match_count,
        )
        logger.debug('Album with closest match: {}'.format(
            most_closely_matched_album[1]))
        logger.debug('Compared to search album: {}'.format(
            album.title
        ))

        if artist_name_word_match_count(most_closely_matched_album) == 0:
            logger.debug('No sufficient match')
            return None
        else:
            logger.debug('Sufficient match!')
            return most_closely_matched_album[0]

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
                WHERE  LOWER(artist)=%s
                  AND  track_count=%s
            ''',
            (
                unidecode(album.artist).lower(),
                album.track_count
            )
        )

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
