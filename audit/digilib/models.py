class DigilibArtist(object):
    # Artist(_id:int_, name:str)
    def __init__(self, db, id, name):
        self.db = db
        self.id = id
        self.name = name

    def __str__(self):
        return self.name


class DigilibAlbum(object):
    # Album(_id:int_, title:str, year:int, filesystem_path:str, artist:int)
    def __init__(self, db, id, title, year, path, artist_id):
        self.db = db
        self.id = id
        self.title = title
        self.year = year
        self.path = path
        self.artist_id = artist_id

        self._artist = None
        self._tracks = None

    @property
    def artist(self):
        if self._artist is None:
            self._artist = self.db.artist_of(self.id)
        return str(self._artist)

    @property
    def track_count(self):
        return len(self.tracks)

    @property
    def tracks(self):
        if self._tracks is None:
            self._tracks = self.db.tracks_of(self.id)
        return self._tracks

    def __str__(self):
        return (
            'Digilib Album: {0.title} ({0.year}) by {0.artist}'
            ' -- {0.track_count} tracks -- {0.path}'
        ).format(self)

    def dict(self):
        return {
            'digilib_title': self.title,
            'digilib_artist': self.artist,
            'digilib_year': self.year,
            'digilib_path': self.path
        }


class DigilibSong(object):
    # Song(_id:int_, title:str, duration:int, track_number:int,
    #      album:int, filesystem_path:int, artist:int)
    def __init__(self, db, id, title, duration, track_number, album_id,
                 path, artist_id):
        self.db = db
        self.id = id
        self.title = title
        self.duration = duration
        self.track_number = track_number
        self.album_id = album_id
        self.path = path
        self.artist_id = artist_id

