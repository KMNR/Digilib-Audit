import mutagen
import os


class SongFile(object):
    def __init__(self, file_path):
        self.path = file_path
        self.filename = os.path.basename(file_path)

        # Extract the song's metadata from the music file
        metadata = mutagen.File(file_path, easy=True)
        print(metadata.keys())
        self.track_number = int(metadata.get('tracknumber', [None])[0])
        self.title = metadata.get('title', [None])[0]
        self.artist = metadata.get('artist', [None])[0]
        self.album = metadata.get('album', [None])[0]
        self.year = int(metadata.get('date', [None])[0])

    def __str__(self):
        return '"{track_number}. {title}" by {artist}' \
               ' off of the album "{album}" ({year})'.format(
            track_number=self.track_number,
            title=self.title,
            artist=self.artist,
            album=self.album,
            year=self.year,
        )
