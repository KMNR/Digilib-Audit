import os

import collections
from unidecode import unidecode


class DigilibArtist(object):
    # Artist(_id:int_, name:str)
    def __init__(self, db, id, name):
        self.db = db
        self.id = id
        self.name = name

    def __str__(self):
        return unidecode(self.name)


class DigilibAlbumFromFiles(object):
    def __init__(self, tracks, path):
        self.tracks = [DigilibSongFromFile(track) for track in tracks]
        self.artist = DigilibArtistFromAlbumTracks(album_tracks=tracks)

        sample_track = self.tracks[0]
        self.metadata_title = sample_track.album
        self.metadata_year = sample_track.year
        self.dir_title = os.path.basename(path)
        self.dir_year = None
        self.path = path
        self.artist_id = None

    def __len__(self):
        return len(self.tracks)

    def __str__(self):
        return '{0.metadata_title} by {0.artist} ({0.metadata_year})'.format(
            self)

    @property
    def attrs(self):
        return {
            'meta_title': self.metadata_title,
            'meta_year': self.metadata_year,
            'fs_title': self.dir_title,
            'fs_year': self.dir_year,
            'path': self.path,
            'artist_id': self.artist_id
        }

    def __iter__(self):
        for track in self.tracks:
            yield track

    @property
    def tracks_tuples(self):
        return [track.attrs for track in self.tracks]

    def set_id(self, id):
        self.id = id
        for track in self.tracks:
            track.album_id = id


class DigilibArtistFromAlbumTracks(object):
    def __init__(self, album_tracks):
        # Artist is either a single artist or 'Various Artists'
        artist_names = self._histogram_of_artist_names(album_tracks)
        most_occuring_artist_name = max(artist_names,
                              key=lambda x: x[1])

        self.metadata_name = most_occuring_artist_name[0]
        self.filesystem_name = 'deadmau5'

    @property
    def attrs(self):
        return {'meta_name': self.metadata_name,
                'fs_name': self.filesystem_name}

    def _histogram_of_artist_names(self, album_tracks):
        artist_name_counts = collections.defaultdict(int)
        for track in album_tracks:
            artist_name_counts[track.artist] += 1

        return list(artist_name_counts.items())

    def __str__(self):
        return self.metadata_name


class DigilibSongFromFile(object):
    def __init__(self, metadata_track):
        self.metadata_track = metadata_track
        self.artist_id = None
        self.album_id = None
        self.year = metadata_track.year
        self.album = metadata_track.album
        self.artist = metadata_track.artist

        self.path = metadata_track.path
        self.filename_title = os.path.basename(self.path)

    @property
    def attrs(self):
        return {
            'meta_title': None,
            'meta_track_number': None,
            'fs_title': self.filename_title,
            'fs_track_number': None,
            'duration': None,
            'path': self.path,
            'artist_id': self.artist_id,
            'album_id': self.album_id
        }


class DigilibAlbum(object):
    # Album(_id:int_, title:str, year:int, filesystem_path:str, artist:int)
    fieldnames = [
        'library_code',
        'klap3id',
        'digilib_title',
        'digilib_artist',
        'digilib_year',
        'digilib_path'
    ]

    def __init__(self, db, id, title, year, path, artist_id):
        self.db = db
        self.id = id
        self.title = title
        self.year = year
        self.path = os.path.dirname(
            path.replace('/media/kp/bobcat/digilib/',''))
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

