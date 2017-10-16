import datetime
import mutagen
import os
import soundfile
import dateutil.parser
import traceback
import json


class SongFile(object):
    metadata_filetype = ('.mp3', '.flac', '.m4a', '.wma')
    filename_scraping_filetypes = ('.wav')

    def __init__(self, file_path):
        self.path = file_path
        self.filename = os.path.basename(file_path)
        self.release_date = None
        self.year = None
        self.artist = None
        self.album = None
        self.duration = None
        self.album_artist = None

        # Extract the song's metadata from the music file
        if file_path.lower()\
                    .endswith(SongFile.metadata_filetype):
            self._initialize_from_mutagen()

        else:
            self._initialize_from_filename()

    def _initialize_from_mutagen(self):
        try:
            metadata = mutagen.File(self.path, easy=True)
        except:
            raise IOError('Problem loading {}'.format(self.path))

        try:
            self.title = metadata.get('title', [None])[0]
            self.artist = metadata.get('artist', [None])[0]
            self.album = metadata.get('album', [None])[0]

            if 'date' in metadata:
                date_string = metadata['date'][0]

                # Edge case: date is set to '0000'
                if date_string == '0000':
                    pass
                else:
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
                self.tracknumber = None

            # Some albums contain tracks from many artists, and resulting
            #  in the album's artist being 'Various Artists'. Record the
            #  album's artist as such.
            self.album_artist = metadata.get('albumartist', [None])[0]

        except KeyboardInterrupt:
            raise

        except Exception as e:
            open('mutagen_errors.txt', 'a').write(
                ('{horizontal_line}\n'
                 '{exception}\n'
                 '{file_path}\n'
                 '{metadata}\n').format(
                     horizontal_line='-'*120,
                     exception=str(e),
                     file_path=self.path,
                     metadata=json.dumps(dict(metadata), indent=4))
            )
            raise e

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

    def _initialize_from_filename(self):
        # Log the .wav file's file path to analyze the patterns in filenames
        with open('wav_files.txt', 'a') as f:
            f.write('{}\n'.format(self.path))

        filename, extension = os.path.splitext(self.filename)

        # Assume the filename is of the format XX TRACKTITLE.ext,
        #  where XX is the track number, TRACKTITLE is the track title,
        #  and ext is the file's extension.
        split_by_spaces = filename.split(' ')
        trackno_string = split_by_spaces[0]
        trackno_string = trackno_string.replace('.', '')
        trackno_string = trackno_string.replace('-', '')
        trackno_string = trackno_string.strip()
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

