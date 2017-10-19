import datetime

from flask import Flask
from flask import render_template
from flask import request

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
        albums = database.get_albums_by_artists(artists=artists)

        albums_by_artist = {
            artist['id']: list() for artist in artists
        }
        for album in albums:
            albums_by_artist[album['artist']].append(album)

        return render_template('artists.html',
                               artists=artists,
                               albums_per_artist=albums_by_artist)

    else:
        artist = database.get_artist(id=artist_id)

        # Load the albums created by this artist.
        albums = database.get_albums_by_artists(artists=[artist])
        albums_by_artist = {
            artist['id']: albums
        }

        # Instead of creating a separate page for displaying one artist vs
        # displaying a bunch of artists, let's just use the same page.
        # To do so, we need to create a singleton list that includes the
        # single artist that we are after.
        return render_template('artists.html',
                               artists=[artist],
                               albums_per_artist=albums_by_artist)


@app.route('/album/')
@app.route('/album/<int:album_id>')
def album_page(album_id=None):
    if album_id is None:
        albums = database.get_all_albums()
        artists = database.get_all_artists()
        songs = database.get_all_songs()

        # This is an example of a dictionary comprehension. It builds a
        # dictionary without having to explicitly use a for-loop.
        artist_names_dictionary = {
            artist['id']: artist['name']
            for artist in artists
        }

        # Build a dictionary of songs associated to each album.
        # First, initialize the dictionary with the album IDs and an empty list.
        songs_by_album_id = {
            album['id']: list()
            for album in albums
        }

        # Once there's an empty list associated for each album, each list can
        # be populated with songs corresponding to each album.
        for song in songs:

            # Some songs do not have an associated album due to poor tags on
            # the sourced music. Skip over these songs.
            if song['album'] is None:
                continue

            album_id = song['album']
            app.logger.debug('Album id: {}'.format(album_id))
            current_song_list = songs_by_album_id[album_id]
            current_song_list.append(song)

        # Then it's a good idea to sort each album list by their track numbers.
        for album_id in songs_by_album_id:
            songs_by_album_id[album_id].sort(key=lambda s: s['track_number'])

        return render_template('albums.html',
                               albums=albums,
                               artist_names=artist_names_dictionary,
                               songs_by_album=songs_by_album_id,
                               album_id=album_id)

    else:
        album = database.get_album(id=album_id)
        artist = database.get_artist(id=album['artist'])
        songs = database.get_songs_from_album(album_id)
        songs_for_album = {album_id: songs}
        return render_template('albums.html',
                               albums=[album],
                               artist_names={artist['id']: artist['name']},
                               album_id=album_id,
                               songs_by_album=songs_for_album)


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
@app.route('/search/artists', methods=['POST'])
def search_artists_by_name():
    artist_name = request.form['artist-name']
    artists = database.get_artists_with_similar_name(name=artist_name)
    albums = database.get_albums_by_artists(artists=artists)

    albums_by_artist = {
        artist['id']: list() for artist in artists
    }
    for album in albums:
        albums_by_artist[album['artist']].append(album)

    return render_template('artists.html',
                           artists=artists,
                           albums_per_artist=albums_by_artist,
                           artist_query=artist_name)


@app.route('/search/albums', methods=['POST'])
def search_albums_by_name():
    album_title = request.form['album-title']
    albums = database.get_albums_with_similar_name(title=album_title)

    # Build a list of unique artist IDs
    artist_ids = set()
    for album in albums:
        artist_ids.add(album['artist'])

    artists = database.get_artists(ids=artist_ids)

    # This is an example of a dictionary comprehension. It builds a
    # dictionary without having to explicitly use a for-loop.
    artist_names_dictionary = {
        artist['id']: artist['name']
        for artist in artists
    }

    return render_template('albums.html',
                           albums=albums,
                           artist_names=artist_names_dictionary)


@app.route('/search/songs', methods=['POST'])
def search_songs_by_name():
    song_title = request.form['song-title']
    songs = database.get_songs_with_similar_name(title=song_title)
    return render_template('songs.html',
                           songs=songs)


# This is a filter used in the HTML template to convert an integer,
# representing seconds, into a timedelta object. This conversion permits the
# displaying of a song's duration as, for example, 0:03:24.
# You'll see it used in the templates as something like
#    {{ track.duration | duration }}
@app.template_filter('duration')
def _jinja2_filter_duration(seconds):
    duration = datetime.timedelta(seconds=seconds)
    return duration
