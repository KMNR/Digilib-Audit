import datetime
import mutagen
import os


class SongFile(object):
    attrs = ['tracknumber', 'title', 'artist', 'album', 'date']
    converters = {
        'tracknumber': int,
        'date': int,
    }

    def __init__(self, file_path):
        self.path = file_path
        self.filename = os.path.basename(file_path)

        # Extract the song's metadata from the music file
        metadata = mutagen.File(file_path, easy=True)
        self.title = metadata.get('title', [None])[0]
        self.artist = metadata.get('artist', [None])[0]
        self.album = metadata.get('album', [None])[0]
        self.date = int(metadata.get('date', [None])[0])

        duration_in_seconds = int(metadata.info.length)
        self.length = datetime.timedelta(seconds=duration_in_seconds)

        # Track number could be a simple number, or XX/NN, where XX is the
        # track number and NN is the total number of tracks.
        tracknumber_string = metadata.get('tracknumber', [None])[0]
        if tracknumber_string:
            if '/' in tracknumber_string:
                trackno, trackcount = tracknumber_string.split('/')
                self.tracknumber = int(trackno)
            else:
                self.tracknumber = int(tracknumber_string)

        # for key in self.attrs:
        #     try:
        #         raw_value = metadata.get(key, [None])[0]
        #
        #         if key in SongFile.converters:
        #             value = SongFile.converters[key](raw_value)
        #         else:
        #             value = raw_value
        #
        #         setattr(self, key, value)
        #     except ValueError:
        #         raise ValueError('Problem with extracting {key}'
        #                          ' from "{path}": value: {value}'.format(
        #             key=key,
        #             value=raw_value,
        #             path=file_path
        #         ))

    def __str__(self):
        return '"{track_number}. {title} ({length})" by {artist}' \
               ' off of the album "{album}" ({year})'.format(
            track_number=self.tracknumber,
            title=self.title,
            length=self.length,
            artist=self.artist,
            album=self.album,
            year=self.date,
        )
