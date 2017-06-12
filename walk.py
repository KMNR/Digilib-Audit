import os
import mutagen

valid_extensions = ('.flac', '.mp3', '.aac', '.ac3', '.dts')
database_filename = 'library.db'

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


Base = declarative_base()
class Song(Base):
    __tablename__ = 'song'

    id = Column(Integer, primary_key=True)
    track_title = Column(String)
    artist = Column(String)
    album = Column(String)
    year = Column(String)
    path = Column(String)

    def __repr__(self):
        return "<Song(title='{0.track_title}', artist='{0.artist}'," \
               " album='{0.album}', year={0.year}, path='{0.path}'>".format(self)


def build_db(dir):
    if not os.path.isdir(dir):
        raise IOError('"{}" is not a directory'.format(dir))

    db_path = os.path.join(dir, database_filename)
    engine = create_engine('sqlite:///{}'.format(db_path))
    Session = sessionmaker(bind=engine)
    db = Session()

    if not os.path.isfile(db_path):
        Base.metadata.create_all(engine)

    else:
        print('Pre-existing database at "{}"'.format(db_path))
        return db

    for directory, subdirectories, files in os.walk(dir):
        for file in files:
            if file.endswith(valid_extensions):
                path = os.path.join(directory, file)

                try:
                    meta = mutagen.File(path, easy=True)
                except:
                    print("Problem parsing file '{}'".format(path))
                    continue

                else:
                    title = meta.get('title', [None])[0] #.encode('ascii', errors='ignore')
                    artist = meta.get('artist', [None])[0] #.encode('ascii', errors='ignore')
                    album = meta.get('album', [None])[0] #.encode('ascii', errors='ignore')
                    year = meta.get('date', [None])[0] #.encodre('ascii', errors='ignore')
                    song = Song(track_title=title,
                                artist=artist,
                                album=album,
                                year=year,
                                path=path)
                    print(song)
                    db.add(song)

        db.commit()

    print()
    return db


if __name__ == '__main__':
    import sys
    build_db(sys.argv[-1])