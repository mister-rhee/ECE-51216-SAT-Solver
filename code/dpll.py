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
    logger.info(f"Row Pointers:             {row_ptr}\n")

    literal_counts = get_literal_counts(values, col_indices, parsed_cnf.nv)
    literal_to_try = select_literal(*literal_counts)
    logger.info(f"Selected literal to try: {literal_to_try}")

# Function that counts the number of positive and negative occurrences of each variable in the CNF formula
def get_literal_counts(values, col_indices, num_literals):
    pos_counts = np.zeros(num_literals, dtype=int)
    neg_counts = np.zeros(num_literals, dtype=int)

    for value, col_index in zip(values, col_indices):
        if value == 1:
            pos_counts[col_index] += 1
        else:
            neg_counts[col_index] += 1

    return pos_counts, neg_counts

# Function that selects the next literal to assign based on the counts of positive and negative occurrences
def select_literal(pos_counts, neg_counts):
    total_counts = pos_counts + neg_counts

    # Get the index (variable ID) of the max value
    # If all are 0, we've likely solved the formula or have an error
    best_var_idx = np.argmax(total_counts)

    # Decide which polarity to return based on which is more frequent
    if pos_counts[best_var_idx] >= neg_counts[best_var_idx]:
        return best_var_idx + 1
    else:
        return -(best_var_idx + 1)

if __name__ == "__main__":
    print("Not meant to be run directly. Please use 'main.py' to execute the program.")
