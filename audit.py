#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNOPSIS

	python audit.py [-h,--help] [-v,--verbose]


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
import db

__appname__ = "digilib-audit"
__author__ = "Doug McGeehan"
__version__ = "0.0pre0"
__license__ = "GNU GPLv3"


import argparse
from datetime import datetime
import sys
import os
import logging

logger = logging.getLogger(__appname__)


def main(args):
    digilib_db = db.DatabaseAPI(db_file_path=config.database_filename)
    klap3_db = db.KLAP3(credentials=config.klap3_credentials)

    # Iterate over each album in digilib (sqlite?)
    # Query KLAP3 for that album using the album's name (mysql)
    # Filter album results in several potential ways:
    #   By artist
    #   By year
    #   By number of tracks
    #   By a combination of all three
    #   Note: there may be two copies of an album in KLAP: one for CDs and
    #    one for Digital
    # Build a list of album IDs that are matched
    # Build a list of album names (with artist names, year, album path) that
    #  are in the digital library but not in KLAP
    # Build a list of KLAP3 albums that are not in the digital library
    # Build a list of digital albums that are in KLAP but not in the digital
    #  library
    pass

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

