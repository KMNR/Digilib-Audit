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
    return render_template('artists.html',
                           artist_id=artist_id)


@app.route('/album/')
@app.route('/album/<int:album_id>')
def album_page(album_id=None):
    return render_template('albums.html',
                           album_id=album_id)


@app.route('/song/')
@app.route('/song/<int:song_id>')
def song_page(song_id=None):
    return render_template('songs.html',
                           song_id=song_id)


################################################################################
# Search by names
#
@app.route('/search/artist/<artist_name>/')
def search_artists_by_name(artist_name):
    return 'Artist %s' % artist_name


@app.route('/search/album/<album_name>/')
def search_albums_by_name(album_name):
    return 'Album %d' % album_name




