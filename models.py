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
        self.album_artist = None
        self.album = None
        self.release_date = None
        self.year = None

    def get_album_info_from_path(self):
        filename, extension = os.path.splitext(self.filename)

        underscore_seperated = ' ' not in filename and '_' in filename
        period_after_track_number = len(filename.split('.')) > 1

        if period_after_track_number:
            # e.g. 10. Something Track.mp3
            split = filename.split(' ')
            split[0] = split[0].replace('.', '')

        elif underscore_seperated:
            # e.g. 10_No_Spaces.mp3
            split = filename.split('_')

        else:
            # Assume the filename is of the format XX TRACKTITLE.ext,
            #  where XX is the track number, TRACKTITLE is the track title,
            #  and ext is the file's extension.
            split = filename.split(' ')

        trackno_string = split[0]
        tracknumber = int(trackno_string)
        title = ' '.join(split[1:])

        # Assume the name of the directory containing this file contains the
        # song's album name and artist in the following format:
        #  ARTIST/ALBUM
        directory = os.path.dirname(self.path)
        album = os.path.basename(directory)
        parent_directory = os.path.dirname(directory)
        artist = os.path.basename(parent_directory)
        return tracknumber, title, album, artist

    def __str__(self):
        return '"{track_number}. {title} ({length})" by {artist}' \
               ' off of the album "{album}" ({year}){album_artist}' \
               ' -- {path}'.format(
            track_number=self.tracknumber,
            title=self.title,
            length=self.length,
            artist=self.artist,
            album=self.album,
            year=self.year,
            path=self.path,
            album_artist=' [{}]'.format(self.album_artist) \
                         if self.album_artist else ''
        )


class MutagenCompatibleSongFile(SongFile):
    def __init__(self, file_path):
        super(MutagenCompatibleSongFile, self).__init__(file_path=file_path)

        metadata = mutagen.File(self.path, easy=True)
        tnumber, title, artist, album = self.get_album_info_from_path()

        self.title = metadata.get('title', [title])[0]
        self.artist = metadata.get('artist', [artist])[0]
        self.album = metadata.get('album', [album])[0]
        self.album_artist = metadata.get('albumartist', [None])[0]

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

        else:
            self.tracknumber = tnumber


class SongWavFile(SongFile):
    def __init__(self, file_path):
        super(SongWavFile, self).__init__(file_path=file_path)

        (self.tracknumber, self.title, 
         self.album, self.artist) = self.get_album_info_from_path()

        self.length = self._extract_song_duration()

    def _extract_song_duration(self):
        # Extract the song's duration from the file
        # Based on this post: https://stackoverflow.com/a/41617943/412495
        sound_file = soundfile.SoundFile(self.path)
        sample_count = len(sound_file)
        sample_rate = sound_file.samplerate
        duration_in_seconds = int(sample_count / sample_rate)

        return datetime.timedelta(seconds=duration_in_seconds)
