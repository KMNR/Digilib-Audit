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
    def __init__(self, id, artist_id, label_id, name, letter, date_entered,
                 missing, album_art_url, mbid, search_slug):
        self.id = id
        self.artist_id = artist_id
        self.label_id = label_id
        self.name = name
        self.letter = letter
        self.date_entered = date_entered
        self.missing = missing
        self.album_art_url = album_art_url
        self.mbid = mbid
        self.search_slug = search_slug

        self.title = name

    def __str__(self):
        return 'KLAP3: {0.title} by artist {0.artist_id}'.format(self)

