#!/usr/bin/env python3

import argparse
import logging
import time
from contextlib import contextmanager

from dimacs_parser import *
from dpll import *

logger = logging.getLogger(__name__)

@contextmanager
def timer(label):
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        logger.info(f"{label} took {end - start:.6f} seconds")

def parse_arguments():
    ## Create a parser instance
    parser = argparse.ArgumentParser()

    ## Add arguments
    # Positional args
    parser.add_argument("input", help="Input CNF path. Can be relative or absolute path", type=str)

    # Optional args
    parser.add_argument("-v", "--verbose", action="store_true", help="Optional flag to enable verbose stdout messages")

    ## Pull the values out of the arguments
    return parser.parse_args()

def main():
    ### Parse main level arguments
    args = parse_arguments()

    ### Configure the logging level and the format
    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = ("%(levelname)s [%(filename)s:%(lineno)d]: %(message)s" if args.verbose else "%(levelname)s: %(message)s")

    logging.basicConfig(level=log_level, format=log_format)

    ### Call dimacs parser
    logger.debug("Calling functions in dimacs_parser.py")
    with timer("DIMACS Parser"):
        cnf = dimacs_parser(args.input)

    ### Call DPLL solver
    logger.debug("Calling functions in dpll.py")
    with timer("DPLL Solver"):
        dpll(cnf)

if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    end_time = time.perf_counter()
    logger.info(f"Execution time: {end_time - start_time:.6f} seconds")