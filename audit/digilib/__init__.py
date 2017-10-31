import sqlite3
import logging
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

        albums = cursor.execute("""
            SELECT Album.title as AlbumTitle
            ,      Artist.name as ArtistName
            ,      COUNT(Song.id) as TrackCount 
            ,      Album.year as Year
            ,      Album.filesystem_path as Path
            FROM Album, Artist, Song
            WHERE Album.artist=Artist.id
              AND Song.album=Album.id
            GROUP BY Song.album
        """)
        for t in albums:
            digilib_album = DigilibAlbum(*t)
            yield digilib_album

        cursor.close()

    def album_count(self):
        cursor = self.connection.cursor()

        cursor.execute('SELECT COUNT(*) FROM Album')
        count, = cursor.fetchone()

        cursor.close()

        return count


class DigilibAlbum(object):
    def __init__(self, title, artist, track_count, year, path):
        self.title = title
        self.artist = artist
        self.track_count = track_count
        self.year = year
        self.path = path

    def __str__(self):
        return (
            'Digilib Album: {0.title} ({0.year}) by {0.artist}'
            ' -- {0.track_count} tracks -- {0.path}'
        ).format(self)
