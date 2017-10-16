from flask import Flask
from flask import render_template

import config
import db
database = db.DatabaseAPI(config.database_filename)

app = Flask(__name__)


@app.route('/')
def index():
    album_count = database.get_artist_count()
    artist_count = database.get_album_count()
    song_count = database.get_song_count()
    duration_of_entire_library = database.get_library_runtime()
    return render_template('index.html',
                           album_count=album_count,
                           artist_count=artist_count,
                           song_count=song_count,
                           duration=duration_of_entire_library)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    app.logger.debug('A value for debugging')
    app.logger.warning('A warning occurred (%d apples)', 42)
    app.logger.error('An error occurred')
    return render_template('hello.html', name=name)


@app.route('/artist/')
@app.route('/artist/<int:artist_id>')
def artist_page(artist_id=None):
    if artist_id is None:
        artists = database.get_all_artists()
        return render_template('artists.html',
                               artists=artists,
                               artist_id=artist_id)

    else:
        artist = database.get_artist(id=artist_id)

        # Instead of creating a separate page for displaying one artist vs
        # displaying a bunch of artists, let's just use the same page.
        # To do so, we need to create a singleton list that includes the
        # single artist that we are after.
        return render_template('artists.html',
                               artists=[artist],
                               artist_id=artist_id)


@app.route('/album/')
@app.route('/album/<int:album_id>')
def album_page(album_id=None):
    if album_id is None:
        albums = database.get_all_albums()
        artists = database.get_all_artists()

        # This is an example of a dictionary comprehension. It builds a
        # dictionary without having to explicitly use a for-loop.
        artist_names_dictionary = {
            artist['id']: artist['name']
            for artist in artists
        }

        return render_template('albums.html',
                               albums=albums,
                               artist_names=artist_names_dictionary,
                               album_id=album_id)

    else:
        album = database.get_album(id=album_id)
        artist = database.get_artist(id=album['artist'])
        return render_template('albums.html',
                               albums=[album],
                               artist_names={artist['id']: artist['name']},
                               album_id=album_id)


@app.route('/song/')
@app.route('/song/<int:song_id>')
def song_page(song_id=None):
    if song_id is None:
        songs = database.get_all_songs()
        return render_template('songs.html',
                               songs=songs)

    else:
        song = database.get_song(id=song_id)
        return render_template('songs.html',
                               songs=[song])


################################################################################
# Search by names
#
@app.route('/search/artists')
def search_artists_by_name(artist_name):
    return 'Artist %s' % artist_name


@app.route('/search/albums')
def search_albums_by_name(album_name):
    return 'Album %d' % album_name


@app.route('/search/songs')
def search_songs_by_name(song_name):
    return 'Song: %d' % song_name


