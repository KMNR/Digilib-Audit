import os
import traceback

import config
import db
import models


def load_songs_from_directory(directory):
    for directory, subdirectories, files in os.walk(directory):
        songs = []
        for file in files:
            if file.lower().endswith(config.valid_extensions):
                path = os.path.join(directory, file)
                try:
                    print(path)
                    if file.lower()\
                           .endswith(config.mutagen_compliant_extensions):
                        song = models.MutagenCompatibleSongFile(file_path=path)
                    else:
                        song = models.SongWavFile(file_path=path)

                except ValueError as e:
                    with open('problems.txt', 'a') as f:
                        f.write(traceback.format_exc())
                        f.write('{}\n'.format(e))
                        f.write('{}\n'.format(path))
                        f.write('-'*120 + '\n')

                    traceback.print_exc()
                    print(e)
                    continue

                else:
                    print(song)
                    songs.append(song)
        yield songs


def build_db(directory):
    if not os.path.isdir(directory):
        raise IOError('"{}" is not a directory'.format(directory))

    database = db.DatabaseLoader(db_file_path=config.database_filename)
    try:
        database.initialize_empty_tables()
    except:
        pass

    # Walk through the given directory and find song files.
    for album_songs in load_songs_from_directory(directory=directory):
        for song in album_songs:
            database.insert_song(song)


if __name__ == '__main__':
    import sys
    build_db(sys.argv[-1])
