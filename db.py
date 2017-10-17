import os
import sqlite3
import datetime


class BaseDatabaseManager(object):
    def __init__(self, db_file_path):
        self.path = db_file_path
        self.connection = sqlite3.connect(db_file_path)


class DatabaseAPI(BaseDatabaseManager):
    def __init__(self, db_file_path):
        super(DatabaseAPI, self).__init__(db_file_path=db_file_path)

        # Instead of accessing attribute values using indices on a tuple,
        # let's instead setup the connection so that we can access attribute
        # values by their name.
        self.connection.row_factory = sqlite3.Row

    def get_artist_count(self):
        cursor = self.connection.cursor()
        count, = cursor.execute('SELECT COUNT(*) FROM Artist')\
                       .fetchone()
        cursor.close()
        return count

    def get_album_count(self):
        cursor = self.connection.cursor()
        count, = cursor.execute('SELECT COUNT(*) FROM Album') \
                       .fetchone()
        cursor.close()
        return count

    def get_song_count(self):
        cursor = self.connection.cursor()
        count, = cursor.execute('SELECT COUNT(*) FROM Song') \
                       .fetchone()
        cursor.close()
        return count

    def get_library_runtime(self):
        cursor = self.connection.cursor()
        duration_in_seconds, = cursor.execute('SELECT SUM(duration) FROM Song')\
                                     .fetchone()
        cursor.close()
        duration = datetime.timedelta(seconds=duration_in_seconds)
        return duration

    def get_all_artists(self):
        cursor = self.connection.cursor()
        artists = cursor.execute('SELECT * FROM Artist').fetchall()
        cursor.close()
        return artists

    def get_artist(self, id):
        cursor = self.connection.cursor()
        artist = cursor.execute('SELECT * FROM Artist WHERE id=:id',
                                {'id': id}).fetchone()
        cursor.close()
        return artist

    def get_artists_with_similar_name(self, name):
        cursor = self.connection.cursor()
        # The WHERE attribute LIKE '%...%' syntax allows you to make
        # search queries on partially-matching attribute values.
        # e.g.
        #    SELECT * FROM Artist WHERE name LIKE '%Snarky%'
        #
        # This query would return the artist "Snarky Puppy" if it exists in
        # the database.
        matching_artists = cursor.execute(
            'SELECT * FROM Artist'
            ' WHERE name LIKE :name',
            {'name': '%{}%'.format(name)}
        ).fetchall()
        cursor.close()
        return matching_artists

    def get_artists(self, ids):
        cursor = self.connection.cursor()

        # Grab all artists that have an ID contained in the IDs collection.
        # The collection needs to be converted into a comma-delimited string,
        #  which is accomplished as follows:

        # First, convert the collection of integers into a collection of strings
        id_strings = [str(id) for id in ids]

        # Then, join all strings in the collection by a comma
        joined_ids = ','.join(id_strings)

        artists = cursor.execute(
            'SELECT * FROM Artist WHERE id IN (:ids)',
            joined_ids
        ).fetchall()

        cursor.close()
        return artists

    def get_all_albums(self):
        cursor = self.connection.cursor()
        albums = cursor.execute('SELECT * FROM Album').fetchall()
        cursor.close()
        return albums

    def get_album(self, id):
        cursor = self.connection.cursor()
        album = cursor.execute('SELECT * FROM Album WHERE id=:id',
                               {'id': id}).fetchone()
        cursor.close()
        return album

    def get_albums_with_similar_name(self, title):
        cursor = self.connection.cursor()
        matching_albums = cursor.execute(
            'SELECT * FROM Album'
            ' WHERE title LIKE :title',
            {'title': '%{}%'.format(title)}
        ).fetchall()
        cursor.close()
        return matching_albums

    def get_all_songs(self):
        cursor = self.connection.cursor()
        songs = cursor.execute('SELECT * FROM Song').fetchall()
        cursor.close()
        return songs

    def get_song(self, id):
        cursor = self.connection.cursor()
        song = cursor.execute('SELECT * FROM Song WHERE id=:id',
                              {'id': id}).fetchone()
        cursor.close()
        return song

    def get_songs_with_similar_name(self, title):
        cursor = self.connection.cursor()
        matching_songs = cursor.execute(
            'SELECT * FROM Song'
            ' WHERE title LIKE :title',
            {'title': '%{}%'.format(title)}
        ).fetchall()
        cursor.close()
        return matching_songs

    def get_albums_by_artists(self, artists):
        cursor = self.connection.cursor()

        # What follows is an example of a list comprehension in Python.
        # It builds a list without the need for a for-loop.
        artist_ids = set([artist['id'] for artist in artists])

        albums = []
        for id in artist_ids:
            # Order the results of the query in descending order by year
            albums_by_artist = cursor.execute(
                'SELECT * FROM Album WHERE artist=:id ORDER BY year DESC',
                {'id': id}
            )
            albums.extend(albums_by_artist.fetchall())

        cursor.close()
        return albums


class DatabaseLoader(BaseDatabaseManager):
    def __init__(self, db_file_path):
        super(DatabaseLoader, self).__init__(db_file_path=db_file_path)

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
            '    id INTEGER PRIMARY KEY,'
            '    title VARCHAR(120) NOT NULL,'
            '    year INTEGER,'     # The year attribute is allowed to be null.
            '    filesystem_path VARCHAR(500) UNIQUE,'
            '    artist INTEGER NOT NULL,'
            '    FOREIGN KEY(artist) REFERENCES Artist(id)'
            ')'
        )
        self.connection.commit()

        print(', Song', end='')
        # Create the Song table
        cursor.execute(
            'CREATE TABLE Song ('
            '    id INTEGER PRIMARY KEY,'
            '    title VARCHAR(120) NOT NULL,'
            '    duration INTEGER,'
            '    track_number INTEGER,'
            '    album INTEGER,'
            '    filesystem_path VARCHAR(500) NOT NULL UNIQUE,'
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
        artist_id = self.find_artist_id(song.artist, cursor)

        # Determine if the song's album already exists in the Album table.
        # If not, add a new album.
        # If the album already exists, query for its primary key.
        album_id = self.find_album_id(song, cursor)

        # Finally, insert the song into the database.
        cursor.execute(
            'INSERT INTO Song'
            ' VALUES (NULL, :title, :duration, :track_number,'
            ' :album, :path, :artist)',
            {
                'title': song.title,
                'duration': song.length.total_seconds(),
                'track_number': song.tracknumber,
                'album': album_id,
                'path': song.path,
                'artist': artist_id,
            }
        )
        self.connection.commit()
        return cursor.lastrowid

    def find_artist_id(self, artist_name, cursor):
        if artist_name is None:
            # The song does not have an artist name associated to it.
            # Skip the search for artist and return None.
            # Later on, we'll consider a None value for the artist's primary key
            #  as meaning a song does not specify its artist.
            return None

        else:
            # The song does specify its artist. First, let's see if this
            # particular artist already exists in the database.
            artist_tuples = cursor.execute(
                'SELECT * FROM Artist WHERE name=:artist',
                {
                    'artist': artist_name
                }
            )
            first_artist_tuple = artist_tuples.fetchone()

            # If no results were returned, the provided artist name does not
            # exist in the database. We'll now insert it, and grab the
            # primary key of that newly inserted artist.
            if first_artist_tuple is None:
                # Insert the artist.
                # If there's an album artist and a song artist, also insert
                # the album artist.
                self.insert_artist(artist_name=artist_name, cursor=cursor)

                # Now extract that artist's unique ID.
                # Here's one way to do so: simply query the database again.
                artist_id_tuples = cursor.execute(
                    'SELECT id FROM Artist WHERE name=:artist',
                    {
                        'artist': artist_name
                    }
                )
                first_artist_tuple = artist_id_tuples.fetchone()
                # Since we only queried for one attribute on the Artist table
                #  - the id attribute - it'll be the first attribute value in
                #  the returned tuple.
                return first_artist_tuple[0]

            else:
                # There exists an artist with the given artist name.
                # Capture it's primary key and save for later.
                return first_artist_tuple[0]

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

    def find_album_id(self, song, cursor):
        # Get the album's path from the directory containing this song.
        album_path = os.path.dirname(song.path)
        # We could use this parameter to search for albums as it qualifies as
        #  a candidate key, but instead I'll use the following methods:
        #       1. query by album, year
        #       2. query by album, artist

        if song.album_artist is not None:
            artist_id = self.find_artist_id(song.album_artist, cursor)
        else:
            artist_id = self.find_artist_id(song.artist, cursor)

        if song.album is None:
            # The song does not have an album name associated to it.
            # Skip the search for album and return None.
            print('{path} does not have an album associated to it'.format(
                path=song.path
            ))
            return None

        elif song.year is not None:
            # The song specifies both its album name and the release year of
            # the album. We'll use both of these attributes to perform our
            # pre-existing album search.
            # We'll structure our query using another approach to building
            # SQL queries: using the ? placeholder.
            album_tuples = cursor.execute(
                'SELECT COUNT(*) FROM Album'
                ' WHERE title=? AND year=?',
                (song.album, song.year)
            )
            album_count_tuple = album_tuples.fetchone()

            # We can unroll the tuple like so. Note that singleton tuples
            # require the lonesome comma.
            (album_count,) = album_count_tuple
            # We could also have just selected the first element of the
            # album_count_tuple like so, but I'm showing you a lot of ways
            # to do things in Python
            # album_count = album_count_tuple[0]

            # If the album count is 0, then the provided album name does not
            # exist in the database. We'll now insert it, and grab the
            # primary key of that newly inserted album.
            if album_count == 0:
                # Insert the album.
                # Take a look at how the new album ID is being extracted in the
                # insert_album() method. It's another way of getting the
                # primary key of a newly-inserted tuple.
                new_album_id = self.insert_album(album_name=song.album,
                                                 album_year=song.year,
                                                 path=song.path,
                                                 artist_id=artist_id,
                                                 cursor=cursor)

                return new_album_id

            else:
                # There exists an album with the given title and year.
                # Capture it's primary key and save for later.
                # Now extract that artist's unique ID.
                album_id_tuples = cursor.execute(
                    'SELECT id FROM Album WHERE title=:album AND year=:year',
                    {
                        'album': song.album,
                        'year': song.year,
                    }
                )
                album_id = album_id_tuples.fetchone()[0]
                return album_id

        else:
            # The song does specify its album, but not its year. Let's see if
            #  this particular album already exists in the database where it's
            #  made by the song's specified artist - multiple artists may create
            #  an album with the same title, so we want to avoid selecting
            # the wrong album. To accomplish this, we need a conditional join.
            artist_name = song.album_artist if song.album_artist\
                                            else song.artist
            album_tuples = cursor.execute(
                'SELECT Album.id as album_id FROM Album'
                ' JOIN Artist ON Album.artist=Artist.id'
                ' WHERE Artist.name="{artist}"'
                ' AND Album.title="{album}"'.format(artist=artist_name,
                                                    album=song.album)
            )
            # In this example, I used Python's string formatting
            #  functionality to construct the query. However, be careful with
            #  this! It may lead to a security vulnerability known as SQL
            #  injection. Don't use this method if you do not trust the source
            #  of the values being queried on - e.g. if they come from user
            #  input or data values created by someone other than yourself.

            album_id_tuple = album_tuples.fetchone()
            if album_id_tuple is None:
                # No album exists in the table. Insert it now.
                new_album_id = self.insert_album(album_name=song.album,
                                                 artist_id=artist_id,
                                                 path=album_path,
                                                 cursor=cursor)
                return new_album_id

            else:
                # The album-artist pairing exists in the database.
                # We can extract the album id using it's attribute name.
                # Notice that we renamed the attribute in the above select
                # query.
                album_id = album_id_tuple[0]
                # We could also have just selected the first element of the
                # album_count_tuple like so, but I'm showing you a lot of ways
                # to do things in Python
                #album_id = album_id_tuple[0]
                return album_id

    def insert_album(self, album_name, artist_id, path, cursor,
                     album_year=None):
        # Add a new album into the database.
        # Notice how this method has "album_year=None". This is an optional
        #  parameter. If this method was called without specifying that
        #  parameter in the method signature, then its value will default to
        #  None. Optional parameters must go after all non-default parameters.
        cursor.execute(
            'INSERT INTO Album'
            ' VALUES (NULL, :title, :year, :path, :artist_foreign_key)',
            {'title': album_name,
             'year': album_year if album_year is not None else 'NULL',
             'path': path,
             'artist_foreign_key': artist_id}
        )
        self.connection.commit()

        # We can grab the primary key of this newly-inserted album like so,
        # without having to execute another query.
        return cursor.lastrowid


if __name__ == '__main__':
    db = DatabaseLoader('music.db')
    db.initialize_empty_tables()

