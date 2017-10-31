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
        'Exact': 'gray',
        'Multiple Matches': 'red',
        'None': 'green'
    }

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
                ' {0.title: ^30} │'
                ' {0.artist: ^30}'
            ).format(self),
            self.color_coding[self.match_status]
        )
