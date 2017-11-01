import logging
logger = logging.getLogger(__name__)

import termcolor


class KLAP3Artist(object):
    pass


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
    header = '\t'.join([
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
    ])

    def __init__(self, id, title, genre_code, artist_number, album_letter,
                 artist, missing_flag, format):
        self.id = id
        self.title = title
        self.library_code = '{}{:0>5}{}'.format(genre_code,
                                                artist_number,
                                                album_letter)
        self.artist = artist
        self.is_missing = bool(missing_flag)
        self.format = format
        self.digilib_album = None
        self.match_status = 'None'


    def __str__(self):
        return 'KLAP3: {0.title} by {0.artist} -- {0.library_code} ({0.format})'.format(self)


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

    def csv(self):
        digitized = 'Yes' if self.digilib_album else ''
        is_missing = 'True' if self.is_missing else 'False'
        values = [digitized, self.id, self.library_code, self.title, 
                  self.artist, self.format, is_missing, self.format,
                  self.match_status]
        if self.digilib_album:
            values.extend([self.digilib_album.title,
                           self.digilib_album.artist,
                           self.digilib_album.year,
                           self.digilib_album.path])
        return '\t'.join(map(str, values))

