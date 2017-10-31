import sys
import os
import shutil
import mutagen
import soundfile
import collections


directory = sys.argv[-1]
audio_file_extensions = ('.wav', '.flac', '.mp3', '.mp4', '.wma', '.m4a', '.dts')
encountered_extensions = collections.defaultdict(int)


with open('weed_out_files.txt', 'w') as f:
    for d, subdir, files in os.walk(directory):
        if d.endswith('__MACOSX'):
            shutil.rmtree(d)
            continue

        for filename in files:
            if not filename.lower().endswith(audio_file_extensions):
                continue

            path = os.path.join(d, filename)
            if filename.lower().endswith('.wav'):
                try:
                    soundfile.SoundFile(path)
                except:
                    f.write('{}\n'.format(path))
                    print(path)

            else:
                try:
                    mutagen.File(path, easy=True)
                except:
                    f.write('{}\n'.format(path))
                    print(path)

