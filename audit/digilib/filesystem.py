import os
import config
import termcolor
import logging

from audit.digilib import metadata, models

logger = logging.getLogger(__name__)

def gather_albums_within(root_directory):
    for directory, subdirectories, files in os.walk(root_directory):
        # Check if there are any files within the current directory that end
        # with an audio file extension
        contains_song_files = any(map(
            lambda f: os.path.splitext(f)[-1]\
                             .lower()\
                             .endswith(config.valid_extensions),
            files
        ))

        # If there are some audio files in the current directory,
        # then interpret this directory as containing and album
        if contains_song_files:
            logger.debug('Album found in {}'.format(
                termcolor.colored(directory, 'cyan')
            ))

            # Isolate audio files from other files
            songs = []
            for file in files:
                if file.lower().endswith(config.valid_extensions):
                    path = os.path.join(directory, file)
                    logger.debug(path)
                    if file.lower()\
                           .endswith(config.mutagen_compliant_extensions):
                        song = metadata.MutagenCompatibleSongFile(
                            file_path=path)
                    else:
                        song = metadata.SongWavFile(file_path=path)
                    songs.append(song)

            # Create an album from the song files
            album = models.DigilibAlbumFromFiles(tracks=songs,
                                                 path=directory)

            logger.debug('-'*120)
            yield album
