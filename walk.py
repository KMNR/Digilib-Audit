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
                        title = meta['title']
                        artist = meta['artist']
                        album = meta['album']

                    #if(meta['title'])

                    #db.execute(''' INSERT INTO files
                    #               VALUES (%s, %s, %s, %s, %s, %s)'''
                    #               % (path, file, title, artist, album,))
    return r

#print
get_files("/Users/cliffmartin/digilib/digilib")
