#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	python perform_audit.py [-h,--help] [-v,--verbose]


DESCRIPTION

	Concisely describe the purpose this script serves.


ARGUMENTS

	-h, --help          show this help message and exit
	-v, --verbose       verbose output


AUTHOR

	Doug McGeehan


LICENSE

	Copyright 2017 Doug McGeehan - GNU GPLv3

"""
import csv
import config
from audit import digilib, klap3
from audit.digilib.models import DigilibAlbum

__appname__ = "audit"
__author__ = "Doug McGeehan"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"


import argparse
from datetime import datetime
import sys
import os
import logging
import termcolor
from audit.klap3.models import KLAP3Album

#import progressbar
#progressbar.streams.wrap_stderr()

logger = logging.getLogger(__appname__)


def main(args):
    digilib_db = digilib.load(db_file_path=config.database_filename)
    klap3_db = klap3.load(credentials=config.klap3_credentials)

    # Create a derived table (can't do materialized views in MySQL) that
    # contains album ID, album name, artist name, album track counts,
    # and library code (as separate attributes for genre abbreviation,
    # artist library number and album letter).
    klap3_db.create_view()

    # TODO: do a better solution for the key error that occurs with some albums
    klap3_albums_hash = {a.id: a for a in klap3_db.albums()}

    orphaned_digital_albums = []
    ghost_digital_albums = [] # extra
    albums_to_digitize = []
    matching_albums = []

    # Iterate over each album in digilib
    unfound_hashmap_albums = []
    digilib_album_count = digilib_db.album_count()
    digitlib_spreadsheet_file = open('digilib_reconnect.csv', 'w')
    digitlib_spreadsheet = csv.DictWriter(
        digitlib_spreadsheet_file,
        fieldnames=DigilibAlbum.fieldnames
    )
    digitlib_spreadsheet.writeheader()
    #progress = progressbar.ProgressBar(max_value=digilib_album_count)
    for i, album in enumerate(digilib_db.albums()):
        #progress.update(i)

        # Query KLAP3 for that album using the album's name (mysql)
        found_album_ids = klap3_db.find(album)

        if found_album_ids:
            # Convert album IDs to matches
            klap3_album_matches = [
                klap3_albums_hash[id] for id in found_album_ids
            ]

            for klap3_album in klap3_album_matches:
                logger.debug(klap3_album)
                klap3_album.digilib_album = album
                matching_albums.append(klap3_album)

                print(' {libcode} │'
                      ' {album: ^60} │'
                      ' {artist: ^60} │'
                      ' {track_count: >2} │'
                      ' {year} │'
                      ' {path}'.format(
                    libcode=termcolor.colored(
                        '{: ^10}'.format(klap3_album.library_code),
                        'green'
                    ),
                    track_count=album.track_count,
                    album=album.title,
                    artist=album.artist,
                    year=album.year,
                    path=album.path
                ))

            if len(found_album_ids)==1:
                klap3_album_matches[0].match_status = 'Exact'
                logger.debug(termcolor.colored('Single match!', 'green'))

            elif len(found_album_ids)>1:
                logger.warning('{} {}'.format(
                    termcolor.colored(str(len(found_album_ids)),
                                      'cyan',
                                      attrs=['underline', 'bold']),
                    termcolor.colored('KLAP3 matches for {}:'.format(album),
                                      'cyan')
                ))

                with open('multiple_album_matches.txt', 'a') as f:
                    f.write('{}\n'.format(album))
                    for klap3_album in klap3_album_matches:
                        klap3_album.match_status = 'Multiple Matches'

                        f.write('{}\n'.format(klap3_album))

                    f.write('\n')

        else:
            logger.debug(termcolor.colored('No matches: {}'.format(album),
                                           'red'))
            print(' {colored_NA} │'
                  ' {dl_album: ^60} │'
                  ' {dl_artist: ^60} │'
                  ' {track_count: >2} │'
                  ' {dl_year} │'
                  ' {path}'.format(
                colored_NA=termcolor.colored(
                    '{: ^10}'.format('N/A'),
                    'red'
                ),
                track_count=album.track_count,
                dl_album=album.title,
                dl_artist=album.artist,
                dl_year=album.year,
                path=album.path
            ))
            orphaned_digital_albums.append(album)

        if found_album_ids:
            for klap3_album_id in found_album_ids:
                klap3_album = klap3_albums_hash[klap3_album_id]
                album_dict = album.dict()
                album_dict.update({
                    'library_code': klap3_album.library_code,
                    'klap3id': klap3_album.id
                })
                digitlib_spreadsheet.writerow(album_dict)
        else:
            album_dict = album.dict()
            album_dict.update({
                'library_code': '',
                'klap3id': ''
            })
            digitlib_spreadsheet.writerow(album_dict)

        logger.debug('')

    # Build a list of album IDs that are matched
    # Build a list of album names (with artist names, year, album path) that
    #  are in the digital library but not in KLAP
    # Build a list of KLAP3 albums that are not in the digital library
    # Build a list of digital albums that are in KLAP but not in the digital
    #  library

    klap3_albums = sorted(klap3_albums_hash.values(),
                          key=lambda a: a.library_code)

    with open('digitization_task.csv', 'w') as digitization_spreadsheet_file:
        digitization_spreadsheet = csv.DictWriter(
            digitization_spreadsheet_file,
            fieldnames=KLAP3Album.fieldnames
        )
        digitization_spreadsheet.writeheader()

        for album in klap3_albums:
            logger.info(album.colored())
            digitization_spreadsheet.writerow(album.dict())

    logger.warning('Unable to find {} KLAP3 albums in initial hashmap:'.format(
        len(unfound_hashmap_albums)
    ))
    for album in unfound_hashmap_albums:
        logger.warning(album)

    # for album in klap3_db.albums_not_in(matching_albums):
    #     albums_to_digitize.append(album)
    #
    # albums_to_digitize.sort(key=lambda a: a.library_code)



def setup_logger(args):
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    log_file = os.path.join('/tmp', __appname__ + '.log')
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    
    # create console handler with a higher log level
    ch = logging.StreamHandler()

    if args.verbose:
        ch.setLevel(logging.DEBUG)
    else:
        ch.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    line_numbers_and_function_name = logging.Formatter(
        "%(levelname)s [ %(pathname)s::%(funcName)s():%(lineno)s ]"
        "%(message)s")
    fh.setFormatter(line_numbers_and_function_name)
    ch.setFormatter(line_numbers_and_function_name)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Description printed to command-line if -h is called."
    )
    # during development, I set default to False so I don't have to keep
    # calling this with -v
    parser.add_argument('-v', '--verbose', action='store_true',
                        default=False, help='verbose output')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    try:
        start_time = datetime.now()

        args = get_arguments()
        setup_logger(args)

        # figure out which argument key is the longest so that all the
        # parameters can be printed out nicely
        logger.debug('Command-line arguments:')
        length_of_longest_key = len(max(vars(args).keys(),
                                        key=lambda k: len(k)))
        for arg in vars(args):
            value = getattr(args, arg)
            logger.debug('\t{argument_key}:\t{value}'.format(
                argument_key=arg.rjust(length_of_longest_key, ' '),
                value=value))

        logger.debug(start_time)

        main(args)

        finish_time = datetime.now()
        logger.debug(finish_time)
        logger.debug('Execution time: {time}'.format(
            time=(finish_time - start_time)
        ))
        logger.debug("#" * 20 + " END EXECUTION " + "#" * 20)

        sys.exit(0)

    except KeyboardInterrupt as e:  # Ctrl-C
        raise e

    except SystemExit as e:  # sys.exit()
        raise e

    except Exception as e:
        logger.exception("Something happened and I don't know what to do D:")
        sys.exit(1)

