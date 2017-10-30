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
            SELECT * FROM album
        """)

        while True:
            t = cursor.fetchone()
            if t is None:
                break

            klap3_album = models.KLAP3Album(*t)
            yield klap3_album

        cursor.close()

    def find(self, album):
        cursor = self.db.cursor()
        results = cursor.execute("""
            SELECT album_id FROM Song
            GROUP BY album_id
            HAVING COUNT(*)=%s
        """, (album.track_count,))

        albums_with_same_track_count = [n for n, in results]

        results = cursor.execute("""
            SELECT album.name as album_name, 
                   CONCAT(genre.abbreviation, artist.lib_number, album.letter) as library_code,
                   album.missing as is_missing,
                   artist.name as artist_name
            FROM album, genre, artist
            WHERE album.id IN %s
              AND artist.genre_id=genre.id
              AND album.artist_id=artist.id
              AND LOWER(album.name)=%s
              AND LOWER(artist.name)=%s
              
        """, (
            albums_with_same_track_count,
            album.title.lower(),
            album.artist.lower()
        ))

        for found_album in results:
            logger.debug(found_album)

        cursor.close()
