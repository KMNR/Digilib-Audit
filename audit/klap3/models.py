import logging

from unidecode import unidecode

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
        'mediums',
        'matching_status',
        'digilib_title',
        'digilib_artist',
        'digilib_year',
        'digilib_path',
    ]

    def __init__(self, db, id, title, artist, track_count, genre,
                 artist_number, album_letter, mediums):
        self.db = db
        self.id = id
        self.title = title
        self.artist = artist
        self.track_count = track_count
        self.library_code = '{}{:0>5}{}'.format(genre,
                                                artist_number,
                                                album_letter)
        # self.format = format
        self.mediums = mediums
        self.digilib_album = None
        self.match_status = 'None'

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
            'mediums': self.mediums,
            'matching_status': self.match_status
        }

        if self.digilib_album:
            values.update(self.digilib_album.dict())

        return values
