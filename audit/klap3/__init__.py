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

        cursor.execute("""
            SELECT album.id,
                   album.name, 
                   CONCAT(genre.abbreviation, artist.lib_number, album.letter),
                   artist.name,
                   album.missing,
                   search_format.short_name
            FROM   album,
                   genre,
                   artist,
                   album_format,
                   search_format
            WHERE  artist.genre_id=genre.id
              AND  album.artist_id=artist.id
              AND  album.id=album_format.album_id 
              AND  album_format.format_id=search_format.id
        """)

        while True:
            t = cursor.fetchone()
            if t is None:
                break

            klap3_album = models.KLAP3Album(*t)
            yield klap3_album

        cursor.close()

    def find(self, album):
        logger.info('Searching KLAP3 for {}'.format(album))
        
        cursor = self.db.cursor()

        # Find album by matching album title, artist name, and track count.
        cursor.execute("""
            SELECT album.id
              FROM album 
              ,    artist
              ,    song
             WHERE LOWER(album.name)=%s
               AND LOWER(artist.name)=%s
               AND album.artist_id=artist.id
               AND album.id=song.album_id
            GROUP BY song.album_id
            HAVING COUNT(song.id)=%s
        """, (
            unidecode(album.title).lower(),
            unidecode(album.artist).lower(),
            album.track_count
        ))

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

