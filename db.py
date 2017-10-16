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

        # Grab a cursor to use for inserts and queries
        cursor = self.connection.cursor()

        # Determine if the song's artist already exists in the Artist table.
        # If not, add a new artist.
        # If the artist already exists in the database, query for its
        # primary key.
        if song.artist is None:
            # The song does not have an artist name associated to it.
            # Skip the search for artist.
            print('{path} does not have an artist associated to it'.format(
                song.path
            ))
            artist_id = None

        else:
            artist_tuples = cursor.execute(
                'SELECT * FROM Artist WHERE name=:artist',
                {
                    'artist': song.artist
                }
            )
            first_artist_tuple = artist_tuples.fetchone()
            if first_artist_tuple is None:
                # Insert the artist
                self.insert_artist(artist_name=song.artist, cursor=cursor)

                # Now extract that artist's unique ID.
                # Here's one way to do so: simply query the database again.
                artist_id_tuples = cursor.execute(
                    'SELECT id FROM Artist WHERE name=:artist',
                    {
                        'artist': song.artist
                    }
                )
                first_artist_tuple = artist_id_tuples.fetchone()
                artist_id = first_artist_tuple[0]

            else:
                # There exists an artist with the given artist name.
                # Capture it's primary key and save for later.
                artist_id = first_artist_tuple[0]

        # Determine if the song's album already exists in the Album table.
        # If not, add a new album.
        # If the album already exists, query for its primary key.

        # Finally, insert the song into the database.

        print('')
        return None

    def insert_artist(self, artist_name, cursor):
        # Add a new artist into the database.
        # Notice how I am specifying the primary key here as NULL instead of
        # a particular value. In relational algebra, this would be illegal.
        # However, most database systems accommodate this and
        # will auto-generating a value unique primary key upon the insertion
        # of a new tuple.
        cursor.execute(
            'INSERT INTO Artist VALUES (NULL, :artist_name)',
            {'artist_name': artist_name}
        )
        self.connection.commit()


if __name__ == '__main__':
    db = DatabaseManager('music.db')
    db.initialize_empty_tables()

