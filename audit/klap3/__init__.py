import MySQLdb
import logging
from audit.klap3 import models

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
        
        cursor.execute("""
            SELECT album.id
              FROM album 
              ,    artist
             WHERE LOWER(artist.name)=%s
               AND LOWER(album.name)=%s
               AND album.artist_id=artist.id
        """, (
            album.title.lower(),
            album.artist.lower()
        ))

        matching_album_ids = [id for id, in cursor.fetchall()]
        logger.debug('{} KLAP3 albums found'.format(len(matching_album_ids)))

        cursor.close()
        logger.debug('')
        return matching_album_ids

