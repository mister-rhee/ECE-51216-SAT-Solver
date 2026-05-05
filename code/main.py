#!/usr/bin/env python3

import argparse
import logging
import time
import globals
from pathlib import Path
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

    # Option to log output to file
    parser.add_argument("-l", "--log", action="store_true", help="Optional flag to log stdout messages to an output file")

    # Option to use MOM
    parser.add_argument("-m", "--mom", action="store_true", help="Run solver with Maximum Occurrence of Minimum Size heuristic")

    ## Pull the values out of the arguments
    return parser.parse_args()

def main():
    ### Parse main level arguments
    globals.args = parse_arguments()

    ### Configure the logging level and the format
    log_level = logging.DEBUG if globals.args.verbose else logging.INFO
    log_format = ("%(levelname)s [%(filename)s:%(lineno)d]: %(message)s" if globals.args.verbose else "%(levelname)s: %(message)s")

    if globals.args.log:
        path_obj = Path(globals.args.input)
        input_filename = path_obj.stem

        output_filename_string = f"log/{input_filename}"
        if globals.args.verbose:
            output_filename_string = output_filename_string + ".v"
        if globals.args.mom:
            output_filename_string = output_filename_string + ".m"

        output_filename_string = output_filename_string + ".log"
        
        logging.basicConfig(
            filename=output_filename_string,
            filemode='w',
            format=log_format,
            level=log_level
        )
    else:
        logging.basicConfig(level=log_level, format=log_format)

    ### Call dimacs parser
    logger.debug("Calling functions in dimacs_parser.py")
    with timer("DIMACS Parser"):
        cnf = dimacs_parser(globals.args.input)

    ### Call DPLL solver
    logger.debug("Calling functions in dpll.py")
    with timer("DPLL Solver"):
        return dpll(cnf)

if __name__ == "__main__":
    start_time = time.perf_counter()
    sat_status, assignments = main()
    end_time = time.perf_counter()
    logger.info(f"Execution time: {end_time - start_time:.6f} seconds")
    if sat_status:
        exit(0)
    else:
        exit(1)