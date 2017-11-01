import logging
logger = logging.getLogger(__name__)

import termcolor


'''
+---------------+--------------+------+-----+---------+----------------+
| Field         | Type         | Null | Key | Default | Extra          |
+---------------+--------------+------+-----+---------+----------------+
| id            | int(11)      | NO   | PRI | NULL    | auto_increment |
| artist_id     | int(11)      | NO   | MUL | NULL    |                |
| label_id      | int(11)      | YES  | MUL | NULL    |                |
| name          | varchar(100) | NO   |     | NULL    |                |
| letter        | varchar(3)   | NO   |     | NULL    |                |
| date_entered  | date         | YES  |     | NULL    |                |
| missing       | tinyint(1)   | NO   |     | NULL    |                |
| album_art_url | varchar(200) | NO   |     | NULL    |                |
| mbid          | varchar(40)  | NO   |     | NULL    |                |
| search_slug   | varchar(100) | NO   | MUL | NULL    |                |
+---------------+--------------+------+-----+---------+----------------+
'''
class KLAP3Album(object):
    color_coding = {
        'Exact': 'grey',
        'Multiple Matches': 'red',
        'None': 'green'
    }
    fieldnames = [
        'digitized',
        'id',
        'library_code',
        'title',
        'artist',
        'format',
        'is_missing',
        'matching_status',
        'digilib_title',
        'digilib_artist',
        'digilib_year',
        'digilib_path',
    ]

    def __init__(self, db, id, artist_id, label_id, name, letter, date_entered,
                 missing, album_art_url, mbid, search_slug):
        self.db = db
        self.id = id
        self.artist_id = artist_id
        self.label_id = label_id
        self.title = name
        self.letter = letter
        self.date_entered = date_entered
        self.is_missing = missing
        self.album_art_url = album_art_url
        self.mbid = mbid
        self.search_slug = search_slug

        self._artist = None
        self._library_code = None
        self._format = None

        self.digilib_album = None
        self.match_status = 'None'

        # self.title = title
        # self.library_code = '{}{:0>5}{}'.format(genre_code,
        #                                         artist_number,
        #                                         album_letter)
        # self.artist = artist
        # self.is_missing = bool(missing_flag)
        # self.format = format

    @property
    def artist(self):
        if self._artist is None:
            self._artist = self.db.artist_of(album=self.id)
        return self._artist.name

    @property
    def library_code(self):
        if self._library_code is None:
            self._library_code = self.db.library_code_of(self.id)
        return self._library_code

    @property
    def format(self):
        if self._format is None:
            self._format = self.db.format_of(self.id)
        return self._format

    def __str__(self):
        return 'KLAP3: {0.title} by {0.artist} ' \
               '-- {0.library_code} ({0.format})'.format(self)


    def colored(self):
        return termcolor.colored(
            (
                ' {0.library_code: <10} │'
                ' {0.title: ^60} │'
                ' {0.artist: ^60} │'
                ' {0.digilib_album}'
            ).format(self),
            self.color_coding[self.match_status]
        )

    def dict(self):
        digitized = 'Yes' if self.digilib_album else ''
        is_missing = 'True' if self.is_missing else 'False'
        values = {
            'digitized': digitized,
            'id': self.id,
            'library_code': self.library_code,
            'title': self.title,
            'artist': self.artist,
            'format': self.format,
            'is_missing': is_missing,
            'matching_status': self.match_status
        }

        if self.digilib_album:
            values.update(self.digilib_album.dict())

        return values

'''
+---------------+------------------+------+-----+---------+----------------+
| Field         | Type             | Null | Key | Default | Extra          |
+---------------+------------------+------+-----+---------+----------------+
| id            | int(11)          | NO   | PRI | NULL    | auto_increment |
| genre_id      | int(11)          | NO   | MUL | NULL    |                |
| name          | varchar(100)     | NO   |     | NULL    |                |
| lib_number    | int(10) unsigned | YES  |     | NULL    |                |
| next_letter   | varchar(3)       | NO   |     | NULL    |                |
| mbid          | varchar(40)      | NO   |     | NULL    |                |
| search_slug   | varchar(100)     | NO   | MUL | NULL    |                |
| riyl          | varchar(255)     | NO   |     | NULL    |                |
| riyl_expires  | date             | YES  |     | NULL    |                |
| differentiate | varchar(100)     | NO   |     | NULL    |                |
+---------------+------------------+------+-----+---------+----------------+
'''
class KLAP3Artist(object):
    def __init__(self, db, id, genre_id, name, lib_number, next_letter, mbid,
                 search_slug, riyl, riyl_expires, differentiate):
        self.db = db
        self.id = id
        self.genre_id = genre_id
        self.name = name
        self.lib_number = lib_number
        self.next_letter = next_letter
        self.mbid = mbid
        self.search_slug = search_slug
        self.riyl = riyl
        self.riyl_expires = riyl_expires
        self.differentiate = differentiate

