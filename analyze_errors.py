import mutagen
import json
import progressbar

file_count = len(open('problems.txt').read().split('\n'))
progress = progressbar.ProgressBar(max_value=file_count)

wav_file_errors_file = open('wav_file_errors.txt', 'w')
mutagen_compatible_file = open('mutagen_file_errors.txt', 'w')
with open('problems.txt') as f:
    for i, file_path in enumerate(f, 1):
        file_path = file_path.replace('\n', '')
        if file_path.lower().endswith('.wav'):
            wav_file_errors_file.write('{}\n'.format(file_path))
        else:
            metadata = mutagen.File(file_path, easy=True)
            mutagen_compatible_file.write('{}\n{}\n'.format(
                '-'*120,
                json.dumps(dict(metadata), indent=4),
            ))

        progress.update(i)

