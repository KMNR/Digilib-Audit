import sqlite3


def create_db(db_file_path):
    print('Initializing music database')

    connection = sqlite3.connect(db_file_path)
    cursor = connection.cursor()

    # Create Artist table
    cursor.execute(
        'CREATE TABLE Artist ('
        '    id INTEGER PRIMARY KEY,'
        '    name VARCHAR(120)'
        ')'
    )

    # Force the database to create the previously created table
    connection.commit()

    # Create Album table
    cursor.execute(
        'CREATE TABLE Album ('
        '    id INTEGER,'
        '    title VARCHAR(120),'
        '    year INTEGER,'
        '    barcode INTEGER,'
        '    catalog_number VARCHAR(20),'
        '    filesystem_path VARCHAR(500),'
        '    artist INTEGER,'
        '    FOREIGN KEY(artist) REFERENCES Artist(id)'
        ')'
    )
    connection.commit()

    # Create the Song table
    cursor.execute(
        'CREATE TABLE Song ('
        '    id INTEGER PRIMARY KEY,'
        '    title VARCHAR(120),'
        '    duration INTEGER,'
        '    track_number INTEGER,'
        '    album INTEGER,'
        '    filesystem_path VARCHAR(500),'
        '    artist INTEGER,'
        '    FOREIGN KEY(album) REFERENCES Album(id),'
        '    FOREIGN KEY(artist) REFERENCES Artist(id)'
        ')'
    )
    connection.commit()

    # Close the cursor before exiting.
    cursor.close()


#
# Base = declarative_base()
# class Song(Base):
#     __tablename__ = 'song'
#
#     id = Column(Integer, primary_key=True)
#     track_title = Column(String)
#     artist = Column(String)
#     album = Column(String)
#     year = Column(String)
#     path = Column(String)
#
#     def __repr__(self):
#         return "<Song(title='{0.track_title}', artist='{0.artist}'," \
#                " album='{0.album}', year={0.year}," \
#                " path='{0.path}'>".format(self)

if __name__ == '__main__':
    create_db('music.db')
