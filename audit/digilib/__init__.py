import sqlite3
import logging

from audit.digilib import models

logger = logging.getLogger(__name__)


def load(db_file_path):
    return DigilibDatabase(db_file_path)


class DigilibDatabase(object):
    def __init__(self, db_file_path):
        self.path = db_file_path
        self.connection = sqlite3.connect(db_file_path)

    def albums(self):
        cursor = self.connection.cursor()
        '''
        Artist(_id:int_, name:str)
        Album(_id:int_, title:str, year:int, filesystem_path:str, artist:int)
        Song(_id:int_, title:str, duration:int, track_number:int, album:int, filesystem_path:int, artist:int)
        '''

        cursor.execute('SELECT * FROM Album')
        for t in cursor:
            yield models.DigilibAlbum(self, *t)

        cursor.close()

    def album_count(self):
        cursor = self.connection.cursor()

        cursor.execute('SELECT COUNT(*) FROM Album')
        count, = cursor.fetchone()

        cursor.close()

        return count

    def artist_of(self, album_id):
        cursor = self.connection.cursor()

        cursor.execute(
            '''
                SELECT * 
                FROM   Artist
                WHERE  Artist.id=(
                       SELECT Album.artist
                       FROM   Album
                       WHERE  Album.id=:album_id
                )
            ''',
            {'album_id': album_id}
        )
        t = cursor.fetchone()

        cursor.close()

        return models.DigilibArtist(self, *t)

    def tracks_of(self, album_id):
        cursor = self.connection.cursor()

        cursor.execute(
            '''
                SELECT * 
                FROM   Song
                WHERE  album=:album_id
            ''',
            {'album_id': album_id}
        )
        T = cursor.fetchmany()

        cursor.close()

        return [models.DigilibSong(self, *t) for t in T]
