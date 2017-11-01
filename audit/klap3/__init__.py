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

    def albums(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM album')

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
                SELECT album.id
                FROM   album 
                ,      artist
                ,      song
                WHERE  LOWER(album.name)=%s
                   AND LOWER(artist.name)=%s 
                   AND album.artist_id=artist.id
                   AND album.id=song.album_id
                GROUP BY song.album_id
                HAVING COUNT(song.id)=%s 
            """,
            (
                unidecode(album.title).lower(),
                unidecode(album.artist).lower(),
                album.track_count
            )
        )

        matching_album_ids = [id for id, in cursor.fetchall()]
        logger.debug('{} KLAP3 albums found'.format(len(matching_album_ids)))

        # if len(matching_album_ids)>1:
        #     logger.debug('Multiple matches found. Querying for CD/CD Singles')
        #     sql = '''
        #         SELECT album_format.album_id
        #           FROM album_format, search_format
        #          WHERE album_format.album_id IN (%s)
        #            AND search_format.short_name IN ('CD', 'CDS')
        #            AND album_format.format_id=search_format.id
        #     ''' % ','.join(['%s'] * len(matching_album_ids))
        #     cursor.execute(sql, tuple(matching_album_ids))
        #
        #     matching_album_ids = [id for id, in cursor.fetchall()]
        #     logger.debug('{} KLAP3 CD/CDS albums found'.format(len(matching_album_ids)))
            
        cursor.close()
        logger.debug('')
        return matching_album_ids

    def artist_of(self, album):
        cursor = self.db.cursor()

        cursor.execute(
            'SELECT * '
            '  FROM artist '
            ' WHERE artist.id=('
            '     SELECT album.artist_id '
            '       FROM album '
            '      WHERE album.id=%s'
            ' )',
            (album,)
        )
        t = cursor.fetchone()
        cursor.close()

        artist = models.KLAP3Artist(self, *t)
        return artist

    def library_code_of(self, album_id):
        cursor = self.db.cursor()
        #     ,      genre.abbreviation
        #     ,      artist.lib_number
        #     ,      album.letter
        cursor.execute(
            '''
                SELECT genre.abbreviation
                ,      artist.lib_number 
                ,      album.letter
                FROM   genre
                ,      artist
                ,      album
                WHERE  album.id=%s
                  AND  album.artist_id=artist.id
                  AND  artist.genre_id=genre.id
            ''',
            (album_id,)
        )
        genre, artist, album = cursor.fetchone()
        cursor.close()

        library_code = '{}{:0>5}{}'.format(genre, artist, album)
        return library_code

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

    def tracks_of(self, album_id):
        cursor = self.db.cursor()

        cursor.execute(
            '''
                SELECT * 
                FROM   song
                WHERE  album_id=%s
            ''',
            (album_id,)
        )
        T = cursor.fetchall()
        logger.debug('{} tracks found for album {}'.format(len(T), album_id))
        cursor.close()

        return [models.KLAP3Song(self, *t) for t in T]
