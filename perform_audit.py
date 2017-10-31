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
import config
from audit import digilib, klap3

__appname__ = "audit"
__author__ = "Doug McGeehan"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"


import argparse
from datetime import datetime
import sys
import os
import logging
import time
import termcolor
import progressbar

progressbar.streams.wrap_stderr()
logger = logging.getLogger(__appname__)


def main(args):
    digilib_db = digilib.load(db_file_path=config.database_filename)
    klap3_db = klap3.load(credentials=config.klap3_credentials)

    klap3_albums_hash = {a.id: a for a in klap3_db.albums()}

    orphaned_digital_albums = []
    ghost_digital_albums = [] # extra
    albums_to_digitize = []
    matching_albums = []

    # Iterate over each album in digilib
    digilib_album_count = digilib_db.album_count()
    progress = progressbar.ProgressBar(max_value=digilib_album_count)
    for i, album in enumerate(digilib_db.albums()):
        progress.update(i)
        logger.info('='*120)

        # Query KLAP3 for that album using the album's name (mysql)
        found_album_ids = klap3_db.find(album)


        if len(found_album_ids)==1:
            klap3_album = klap3_albums_hash[found_album_ids[0]]

            matching_albums.append(klap3_album)
            klap3_album.digilib_album = album
            klap3_album.match_status = 'Exact'

            logger.debug(termcolor.colored('Single match!', 'green'))
            logger.debug(klap3_album)
            logger.debug(album)

        elif len(found_album_ids)>1:
            # Convert album IDs to matches
            klap3_album_matches = [
                klap3_albums_hash[id] for id in found_album_ids
            ]

            logger.warning('{} {}'.format(
                termcolor.colored(str(len(found_album_ids)),
                                  'cyan', 
                                  attrs=['underline', 'bold']),
                termcolor.colored('KLAP3 matches for {}:'.format(album),
                                  'cyan')
            ))
            for klap3_album in klap3_album_matches:
                logger.debug(klap3_album)
                klap3_album.digilib_album = album
                klap3_album.match_status = 'Multiple Matches'
                matching_albums.append(klap3_album)
            time.sleep(10)

        else:
            logger.debug(termcolor.colored('No matches: {}'.format(album), 
                                           'red'))
            orphaned_digital_albums.append(album)

        logger.debug('')

    """
    # Build a list of album IDs that are matched
    # Build a list of album names (with artist names, year, album path) that
    #  are in the digital library but not in KLAP
    # Build a list of KLAP3 albums that are not in the digital library
    # Build a list of digital albums that are in KLAP but not in the digital
    #  library

    klap3_albums = sorted(klap3_albums_hash.values(),
                          key=lambda a: a.library_code)
    for album in klap3_albums:
        logger.info(album.colored())

    # for album in klap3_db.albums_not_in(matching_albums):
    #     albums_to_digitize.append(album)
    #
    # albums_to_digitize.sort(key=lambda a: a.library_code)

    pass
    """


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

