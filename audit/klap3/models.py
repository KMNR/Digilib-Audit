import logging
logger = logging.getLogger(__name__)


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
    def __init__(self, id, title, library_code, artist, missing_flag):
        self.id = id
        self.title = title
        self.library_code = library_code
        self.artist = artist
        self.is_missing = bool(missing_flag)

    def __str__(self):
        return 'KLAP3: {0.title} by {0.artist} -- {0.library_code}'.format(self)

