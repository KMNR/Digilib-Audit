import datetime
import mutagen
import os
import soundfile


class SongFile(object):
    metadata_filetype = ('.mp3', '.flac', '.m4a', '.wma')
    filename_scraping_filetypes = ('.wav')

    attrs = ['tracknumber', 'title', 'artist', 'album', 'date']
    converters = {
        'tracknumber': int,
        'date': int,
    }

    def __init__(self, file_path):
        self.path = file_path
        self.filename = os.path.basename(file_path)

        # Extract the song's metadata from the music file
        if file_path.lower()\
                    .endswith(SongFile.metadata_filetype):
            self._initialize_from_mutagen()

        else:
            self._initialize_from_filename()

    def _initialize_from_mutagen(self):
        metadata = mutagen.File(self.path, easy=True)
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
               ' off of the album "{album}" ({year}) -- {path}'.format(
            track_number=self.tracknumber,
            title=self.title,
            length=self.length,
            artist=self.artist,
            album=self.album,
            year=self.date,
            path=self.path
        )

    def _initialize_from_filename(self):
        filename, extension = os.path.splitext(self.filename)

        # Assume the filename is of the format XX TRACKTITLE.ext,
        #  where XX is the track number, TRACKTITLE is the track title,
        #  and ext is the file's extension.
        split_by_spaces = filename.split(' ')
        trackno_string = split_by_spaces[0]
        self.tracknumber = int(trackno_string)
        self.title = ' '.join(split_by_spaces[1:])

        # Assume the name of the directory containing this file contains the
        # song's album name and artist in the following format:
        #  ARTIST/ALBUM
        directory = os.path.dirname(self.path)
        self.album = os.path.basename(directory)
        parent_directory = os.path.dirname(directory)
        self.artist = os.path.basename(parent_directory)

        # Extract the song's duration from the file
        # Based on this post: https://stackoverflow.com/a/41617943/412495
        sound_file = soundfile.SoundFile(self.path)
        sample_count = len(sound_file)
        sample_rate = sound_file.samplerate
        duration_in_seconds = int(sample_count / sample_rate)
        self.length = datetime.timedelta(seconds=duration_in_seconds)
