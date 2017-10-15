import os
import db
import mutagen

import models

valid_extensions = ('.flac', '.mp3', '.aac', '.ac3', '.dts', '.wav')
database_filename = 'music_library.db'


def load_songs_from_directory(directory):
    songs = []
    for directory, subdirectories, files in os.walk(dir):
        for file in files:
            if file.lower().endswith(valid_extensions):
                path = os.path.join(directory, file)

                try:
                    song = models.SongFile(file_path=path)

                except ValueError:
                    open('problems.txt', 'a').write('{}\n'.format(path))
                    print("!! Problem parsing file '{}'".format(path))
                    continue

                else:
                    print(song)
                    songs.append(song)
    return songs


def build_db(dir):
    if not os.path.isdir(dir):
        raise IOError('"{}" is not a directory'.format(dir))

    db.create_db(db_file_path=database_filename)

    songs = load_songs_from_directory(directory=dir)


if __name__ == '__main__':
    import sys
    #build_db(sys.argv[-1])
    build_db('/home/kp/Music/deadmau5')
