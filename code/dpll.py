#!/usr/bin/env python3

import logging
import numpy as np

logger = logging.getLogger(__name__)

def dpll(parsed_cnf):
    for term in parsed_cnf.clauses:
        logger.debug(term)

    values = []
    col_indices = []
    row_ptr = [0]

    for clause in parsed_cnf.clauses:
        for literal in clause:
            if literal > 0:
                values.append(1)
            else:
                values.append(-1)

            col_indices.append(abs(literal) - 1) # 0-indexed variable ID

        # The new pointer is the current total length of 'values'
        row_ptr.append(len(values))

    logger.info(f"Length of Values Array:   {len(values)}")
    logger.info(f"Values:                   {values}\n")

    logger.info(f"Length of Column Array:   {len(col_indices)}")
    logger.info(f"Column Indices:           {col_indices}\n")

    logger.info(f"Length of Row Array:      {len(row_ptr)}")
    logger.info(f"Row Pointers:             {row_ptr}")

if __name__ == "__main__":
    print("Not meant to be run directly. Please use 'main.py' to execute the program.")
