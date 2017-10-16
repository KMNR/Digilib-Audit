import sys
import os
import shutil

directory = sys.argv[-1]

for d, subdir, files in os.walk(directory):
    if d.endswith('__MACOSX'):
        print(d)
        shutil.rmtree(d)

