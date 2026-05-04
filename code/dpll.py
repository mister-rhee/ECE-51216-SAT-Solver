#!/usr/bin/env python3

import logging
import numpy as np
# from main import timer
import moms
import globals

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
        
    # Convert the arrays to numpy arrays for efficiency
    values = np.array(values, dtype=np.int8)
    col_indices = np.array(col_indices, dtype=np.int32)
    row_ptr = np.array(row_ptr, dtype=np.int32)

    logger.debug(f"Length of Values Array:   {len(values)}")
    logger.debug(f"Values:                   {values}\n")

    logger.debug(f"Length of Column Array:   {len(col_indices)}")
    logger.debug(f"Column Indices:           {col_indices}\n")

    logger.debug(f"Length of Row Array:      {len(row_ptr)}")
    logger.debug(f"Row Pointers:             {row_ptr}\n")

    # Kick off the recursive search
    logger.debug(f"Starting recursive dpll_step call.")
    is_sat, all_assignments = dpll_step(values, col_indices, row_ptr, parsed_cnf.nv, [], 0)

    if is_sat:
        logger.info(f"Formula is SAT. Assignments: {all_assignments}")
        return True, all_assignments
    else:
        logger.info("Formula is UNSAT.")
        return False, []

# Recursive function implementing the DPLL algorithm
#   Returns the status and the assignments made so far
def dpll_step(values, col_indices, row_ptr, num_vars, assignments, recursion_level):

    # Boolean constraint propogation. Force unit-clause assignments until there aren't any unit-clauses
    bcp_assignments = []
    while True:
        unit_literals = find_unit_clauses(row_ptr, col_indices, values)
        if not unit_literals:
            break

        forced_literal = unit_literals[0]
        logger.debug(f"R{recursion_level}. BCP forced literal: {forced_literal}")

        values, col_indices, row_ptr, conflict = simplify_cnf(values, col_indices, row_ptr, forced_literal)
        bcp_assignments.append(forced_literal)

        # BCP choices led to a conflict
        if conflict:
            logger.debug(f"R{recursion_level}. BCP conflict.")
            return False, []

        if len(row_ptr) == 1: # All clauses satisfied by BCP
            return True, assignments + bcp_assignments

    # Need a new variable so as to not overwrite the higher recursion level's value
    current_total_assignments = assignments + bcp_assignments

    literal_to_try = get_next_literal(values, col_indices, row_ptr, num_vars)

    # Quick check if all clauses satisfied (No literals left to pick)
    if literal_to_try is None:
        return True, current_total_assignments

    # Try the selected literal
    logger.debug(f"R{recursion_level}. Trying to remove {literal_to_try}")
    nxt_values, nxt_col_indices, nxt_row_ptr, conflict = simplify_cnf(values, col_indices, row_ptr, literal_to_try)

    if not conflict:
        # Check if formula is empty (SAT)
        if len(nxt_row_ptr) == 1:
            return True, current_total_assignments + [literal_to_try]

        # Recurse deeper
        sat, final_assignments = dpll_step(nxt_values, nxt_col_indices, nxt_row_ptr, num_vars, current_total_assignments + [literal_to_try], recursion_level+1)
        if sat:
            return True, final_assignments

    # Backtrack if there was a conflict. Try the exact opposite assignment
    negated_literal = -literal_to_try
    logger.debug(f"R{recursion_level}. Backtracking: Trying {negated_literal} instead of {literal_to_try}")

    nxt_values, nxt_col_indices, nxt_row_ptr, conflict = simplify_cnf(values, col_indices, row_ptr, negated_literal)

    if not conflict:
        if len(nxt_row_ptr) == 1:
            return True, current_total_assignments + [negated_literal]

        return dpll_step(nxt_values, nxt_col_indices, nxt_row_ptr, num_vars, current_total_assignments + [negated_literal], recursion_level+1)

    # Both branches failed
    return False, []

# Removes the target literal from the current arrays. Uses index masks for efficiency
def simplify_cnf(values, col_indices, row_ptr, assignment):
    target_var = abs(assignment) - 1
    target_pol = 1 if assignment > 0 else -1

    # Find where the literal being removed lives in the col_indices array
    var_locs = np.where(col_indices == target_var)[0]

    # Find the clauses that the literal locations belong to
    affected_clause_ids = np.searchsorted(row_ptr, var_locs, side='right') - 1

    # Determine which clauses are satisfied and which literals are removed
    pols = values[var_locs]
    satisfied_clause_mask = np.zeros(len(row_ptr) - 1, dtype=bool)

    # Mark clauses containing the literal with the correct polarity as satisfied
    sat_ids = affected_clause_ids[pols == target_pol]
    satisfied_clause_mask[sat_ids] = True

    # Create a mask for all literals in the formula
    #   We want to keep literals that are not in a satisfied clause and are not the negated assignment
    literal_mask = np.ones(len(values), dtype=bool)

    # Remove the negated assignment literals (the ones that became False)
    literal_mask[var_locs[pols != target_pol]] = False

    # Broaden the mask: remove ALL literals belonging to satisfied clauses
    # We use a bit of broadcast logic here
    # Repeat the satisfied_clause_mask for each literal in those clauses
    clause_lengths = np.diff(row_ptr)
    full_sat_mask = np.repeat(satisfied_clause_mask, clause_lengths)
    literal_mask[full_sat_mask] = False

    # Extract the new formula
    new_values = values[literal_mask]
    new_col_indices = col_indices[literal_mask]

    # Rebuild row_ptr using the lengths of remaining literals in unsatisfied clauses
    #   We only care about counts in clauses that weren't satisfied
    remaining_lit_counts = np.bincount(np.repeat(np.arange(len(row_ptr)-1), clause_lengths)[literal_mask], minlength=len(row_ptr)-1)

    # If an unsatisfied clause has 0 literals, it's a conflict
    if np.any((remaining_lit_counts == 0) & (~satisfied_clause_mask)):
        return None, None, None, True

    # Only keep counts for clauses that aren't satisfied yet
    active_counts = remaining_lit_counts[~satisfied_clause_mask]
    new_row_ptr = np.zeros(len(active_counts) + 1, dtype=np.int32)
    new_row_ptr[1:] = np.cumsum(active_counts)

    return new_values, new_col_indices, new_row_ptr, False

# Selects the next literal to assign based on how often it appears
def get_next_literal(values, col_indices, row_ptr, num_vars):
    pos_counts, neg_counts = get_literal_counts(values, col_indices, num_vars)

    # Check if we actually have any counts left (total_counts > 0)
    if np.any(pos_counts + neg_counts):
        return select_literal(pos_counts, neg_counts)
    else:
        return None

# Searches the CNF for unit-clauses
def find_unit_clauses(row_ptr, col_indices, values):
    unit_literals = []
    for i in range(len(row_ptr) - 1):
        if (row_ptr[i+1] - row_ptr[i]) == 1:
            idx = row_ptr[i]
            literal = (col_indices[idx] + 1) * values[idx]
            unit_literals.append(literal)
    return unit_literals

# Counts the occurrence of a literal in the CNF
def get_literal_counts(values, col_indices, num_literals):
    # Create masks for positive and negative literals
    pos_mask = (values == 1)
    neg_mask = (values == -1)

    pos_counts = np.bincount(col_indices[pos_mask], minlength=num_literals)
    neg_counts = np.bincount(col_indices[neg_mask], minlength=num_literals)

    return pos_counts, neg_counts

# Returns the most-recurring literal for now.
#   Once conflict-driven learning is implemented, we'll probably weigh the learned clauses more heavily
def select_literal(pos_counts, neg_counts):
    if globals.args.mom:
        return moms.calculate_score(pos_counts, neg_counts)

    total_counts = pos_counts + neg_counts
    best_var_idx = np.argmax(total_counts)

    if pos_counts[best_var_idx] >= neg_counts[best_var_idx]:
        return int(best_var_idx + 1)
    else:
        return int(-(best_var_idx + 1))

if __name__ == "__main__":
    print("Not meant to be run directly. Please use 'main.py' to execute the program.")
