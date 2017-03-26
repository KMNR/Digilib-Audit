import os
import sqlite3
import mutagen

# files (path text, filename text, songname text, artist text, album text, year integer)
db = sqlite3.connect('digilib.db')

def get_files(dir):
    r = []
    subdirs = [x[0] for x in os.walk(dir)]
    for subdir in subdirs:
        files = os.walk(subdir).next()[2]
        if (len(files) > 0):
            for file in files:
                if(file[0] != '.'):
                    path = subdir + "/" + file
                    r.append(path)

                    meta = mutagen.File(path, easy=True)

                    if(meta is None):
                        print "None"
                    else:
                        #print meta.keys()
                        title = meta['title'][0].encode('ascii', errors='ignore')
                        artist = meta['artist'][0].encode('ascii', errors='ignore')
                        album = meta['album'][0].encode('ascii', errors='ignore')
                        try:
                            year = meta['date'][0].encode('ascii', errors='ignore')
                        except KeyError:
                            year = 0

                        query = """ INSERT INTO files VALUES ("%s", "%s", "%s", "%s", "%s", %s);""" % (path, file, title, artist, album, year)
                        print query
                        db.execute(query)

        db.commit()
    return r

#print
get_files("/Users/cliffmartin/digilib/digilib")

db.close()
