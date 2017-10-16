import os
import traceback

import config
import db
import models


def load_songs_from_directory(directory):
    songs = []
    for directory, subdirectories, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(config.valid_extensions):
                path = os.path.join(directory, file)
                try:
                    if file.lower()\
                           .endswith(config.mutagen_compliant_extensions):
                        song = models.MutagenCompatibleSongFile(file_path=path)
                    else:
                        song = models.SongWavFile(file_path=path)

                except ValueError as e:
                    open('problems.txt', 'a').write('{}\n'.format(path))
                    traceback.print_exc()
                    print(e)
                    continue

                else:
                    print(song)
                    songs.append(song)

    return songs


def build_db(directory):
    if not os.path.isdir(directory):
        raise IOError('"{}" is not a directory'.format(directory))

    database = db.DatabaseLoader(db_file_path=config.database_filename)
    database.initialize_empty_tables()

    # Walk through the given directory and find song files.
    songs = load_songs_from_directory(directory=directory)

    # Save the found song data to the database.
    for song in songs:
        database.insert_song(song)


if __name__ == '__main__':
    import sys
    build_db(sys.argv[-1])
