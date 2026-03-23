#!/usr/bin/env python

import argparse
from dimacs_parser import *

def main():
    ### Parse main level arguments
    ## Create a parser instance
    parser = argparse.ArgumentParser()

    ## Add arguments
    # Positional args
    parser.add_argument("input")

    ## Pull the values out of the arguments
    args = parser.parse_args()

    ### Call dimacs parser
    cnf = dimacs_parser(args.input)
    print_parsed_data(cnf)

if __name__ == "__main__":
    main()