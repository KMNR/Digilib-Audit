import sqlite3


class DatabaseManager(object):
    def __init__(self, db_file_path):
        self.path = db_file_path
        self.connection = sqlite3.connect(db_file_path)

    def initialize_empty_tables(self):
        print('Initializing empty tables: ', end='')

        cursor = self.connection.cursor()

        # Create Artist table
        print('Artist', end='')
        cursor.execute(
            'CREATE TABLE Artist ('
            '    id INTEGER PRIMARY KEY,'
            '    name VARCHAR(120)'
            ')'
        )

        # Force the database to create the previously created table
        self.connection.commit()

        # Create Album table
        print(', Album', end='')
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
        self.connection.commit()

        print(', Song', end='')
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
        self.connection.commit()

        # Close the cursor before exiting.
        print('... empty table created at {}!'.format(self.path))
        cursor.close()

    def insert_song(self, song):
        print('Inserting new song: {}'.format(song))

        # Determine if the song's artist already exists in the Artist table.
        # If not, add a new artist.
        # If the artist already exists in the database, query for its primary key.

        # Determine if the song's album already exists in the Album table.
        # If not, add a new album.
        # If the album already exists, query for its primary key.

        # Finally, insert the song into the database.


        print('')
        return None


if __name__ == '__main__':
    db = DatabaseManager('music.db')
    db.initialize_empty_tables()

