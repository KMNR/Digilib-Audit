from flask import Flask
from flask import render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


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
    return 'Artist %s' % artist_id

@app.route('/album/')
@app.route('/album/<int:album_id>')
def album_page(album_id=None):
    return 'Album %d' % album_id


################################################################################
# Search by names
#
@app.route('/search/artist/<artist_name>/')
def search_artists_by_name(artist_name):
    return 'Artist %s' % artist_name


@app.route('/search/album/<album_name>/')
def search_albums_by_name(album_name):
    return 'Album %d' % album_name




