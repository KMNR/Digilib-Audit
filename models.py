import datetime
import mutagen
import os
import soundfile
import dateutil.parser


class SongFile(object):
    def __init__(self, file_path):
        self.path = file_path
        self.filename = os.path.basename(file_path)

        self.tracknumber = None
        self.title = None
        self.length = None
        self.artist = None
        self.album = None
        self.release_date = None
        self.year = None

    def __str__(self):
        return '"{track_number}. {title} ({length})" by {artist}' \
               ' off of the album "{album}" ({year}) -- {path}'.format(
            track_number=self.tracknumber,
            title=self.title,
            length=self.length,
            artist=self.artist,
            album=self.album,
            year=self.year,
            path=self.path
        )


class MutagenCompatibleSongFile(SongFile):
    def __init__(self, file_path):
        super(MutagenCompatibleSongFile, self).__init__(file_path=file_path)

        metadata = mutagen.File(self.path, easy=True)
        self.title = metadata.get('title', [None])[0]
        self.artist = metadata.get('artist', [None])[0]
        self.album = metadata.get('album', [None])[0]

        if 'date' in metadata:
            date_string = metadata['date'][0]
            self.release_date = dateutil.parser.parse(date_string)
            self.year = int(self.release_date.year)

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



class SongWavFile(SongFile):
    def __init__(self, file_path):
        super(SongWavFile, self).__init__(file_path=file_path)

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

        self.length = self._extract_song_duration()

    def _extract_song_duration(self):
        # Extract the song's duration from the file
        # Based on this post: https://stackoverflow.com/a/41617943/412495
        sound_file = soundfile.SoundFile(self.path)
        sample_count = len(sound_file)
        sample_rate = sound_file.samplerate
        duration_in_seconds = int(sample_count / sample_rate)

        return datetime.timedelta(seconds=duration_in_seconds)
