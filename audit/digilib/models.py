"""
Artist(_id:int_, name:str)
Album(_id:int_, title:str, year:int, filesystem_path:str, artist:int)
Song(_id:int_, title:str, duration:int, track_number:int, album:int, filesystem_path:int, artist:int)
"""

class Artist(object):
    def __init__(self):
        self.id = None
        self.name = None


class Album(object):
    def __init__(self):
        self.id = None
        self.title = None
        self.year = None
        self.filesystem_path = None
        self.artist = None


class Song(object):
    def __init__(self):
        self.id = None
        self.title = None
        self.duration = None
        self.track_number = None
        self.album = None
        self.filesystem_path = None
        self.artist = None
