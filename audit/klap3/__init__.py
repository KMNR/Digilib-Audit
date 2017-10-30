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
                   album.missing
            FROM   album, genre, artist
            WHERE  artist.genre_id=genre.id
              AND  album.artist_id=artist.id
        """)

        while True:
            t = cursor.fetchone()
            if t is None:
                break

            klap3_album = models.KLAP3Album(*t)
            yield klap3_album

        cursor.close()

    def find(self, album):
        logger.info('='*120)
        logger.info('Searching KLAP3 for {}'.format(album))

        cursor = self.db.cursor()
        
        cursor.execute("""
            SELECT album.id as album_id,
                   album.name as album_name, 
                   CONCAT(genre.abbreviation, artist.lib_number, album.letter) as library_code,
                   artist.name as artist_name,
                   album.missing as is_missing
             FROM album, genre, artist
            WHERE artist.genre_id=genre.id
              AND album.artist_id=artist.id
              AND LOWER(album.name)=%s
              AND LOWER(artist.name)=%s
              
        """, (
            album.title.lower(),
            album.artist.lower()
        ))

        while True:
            t = cursor.fetchone()
            if t is None:
                break

            logger.debug(t)

        cursor.close()
        logger.debug('')

