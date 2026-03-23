#!/usr/bin/env python3

import argparse
import logging

from dimacs_parser import *

logger = logging.getLogger(__name__)

def main():
    ### Parse main level arguments
    ## Create a parser instance
    parser = argparse.ArgumentParser()

    ## Add arguments
    # Positional args
    parser.add_argument("input", help="Input CNF path. Can be relative or absolute path", type=str)

    # Optional args
    parser.add_argument("-v", "--verbose", action="store_true", help="Optional flag to enable verbose stdout messages")

    ## Pull the values out of the arguments
    args = parser.parse_args()

    ## Configure the logging level and the format
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = ("%(levelname)s [%(filename)s:%(lineno)d]: %(message)s" if args.verbose else "%(levelname)s: %(message)s")

    logging.basicConfig(level=log_level, format=log_format)

    ### Call dimacs parser
    logger.debug("Calling functions in dimacs_parser.py")
    cnf = dimacs_parser(args.input)
    print_parsed_data(cnf)

if __name__ == "__main__":
    main()