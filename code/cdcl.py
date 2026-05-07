#!/usr/bin/env python3

import logging
import numpy as np
import dpll

logger = logging.getLogger(__name__)

use_moms_heuristic = False

def cdcl(parsed_cnf):
    for term in parsed_cnf.clauses:
        logger.debug(term)

    values = []
    col_indices = []
    row_ptr = [0]

    for clause in parsed_cnf.clauses:
        for literal in clause:
            values.append(1 if literal > 0 else -1)
            col_indices.append(abs(literal) - 1)
        row_ptr.append(len(values))

    values = np.array(values, dtype=np.int8)
    col_indices = np.array(col_indices, dtype=np.int32)
    row_ptr = np.array(row_ptr, dtype=np.int32)

    logger.debug(f"Starting CDCL solve.")
    is_sat, all_assignments = cdcl_solve(values, col_indices, row_ptr, parsed_cnf.nv)

    if is_sat:
        logger.info(f"Formula is SAT. Assignments: {all_assignments}")
        print("RESULT:SAT")
        dpll.print_assignments(all_assignments)
        return True, all_assignments
    else:
        logger.info("Formula is UNSAT.")
        print("RESULT:UNSAT")
        return False, []


# Main CDCL loop - iterative instead of recursive so we can backjump freely
def cdcl_solve(values, col_indices, row_ptr, num_vars):
    assignment = np.zeros(num_vars, dtype=np.int8)  # 0=unassigned, 1=pos, -1=neg
    assigned = np.zeros(num_vars, dtype=bool)

    trail = []      # (literal, decision_level, reason_clause_idx)
    trail_lim = [0] # trail_lim[level] = trail index where that level starts

    var_level = np.full(num_vars, -1, dtype=np.int32)
    var_reason = [None] * num_vars  # None means it was a decision

    decision_level = 0

    while True:
        conflict_idx = cdcl_bcp(values, col_indices, row_ptr, assignment, assigned,
                                 trail, var_level, var_reason, decision_level)

        if conflict_idx is not None:
            if decision_level == 0:
                logger.debug("Conflict at level 0: UNSAT.")
                return False, []

            learned_clause, backjump_lvl = analyze_conflict(
                conflict_idx, trail, trail_lim, var_level, var_reason,
                values, col_indices, row_ptr, decision_level)
            logger.debug(f"L{decision_level}. Conflict. Learned: {learned_clause}, backjump to L{backjump_lvl}")

            values, col_indices, row_ptr = add_learned_clause(values, col_indices, row_ptr, learned_clause)
            learned_clause_idx = len(row_ptr) - 2

            backjump(backjump_lvl, assignment, assigned, trail, trail_lim, var_level, var_reason)
            decision_level = backjump_lvl

            # The learned clause is now a unit clause - force the UIP literal
            uip_lit = _find_uip_in_learned(learned_clause, assigned)
            if uip_lit is None:
                return False, []

            logger.debug(f"L{decision_level}. Asserting UIP literal: {uip_lit}")
            _assign(uip_lit, decision_level, learned_clause_idx,
                    assignment, assigned, trail, var_level, var_reason)

        else:
            lit = pick_literal(values, col_indices, assignment, assigned, num_vars)

            if lit is None:
                return True, _build_result(assignment, num_vars)

            decision_level += 1
            trail_lim.append(len(trail))
            logger.debug(f"L{decision_level}. Decision: {lit}")
            _assign(lit, decision_level, None, assignment, assigned, trail, var_level, var_reason)


# BCP - scans all clauses and forces unit literals until no more are found or a conflict occurs
def cdcl_bcp(values, col_indices, row_ptr, assignment, assigned, trail,
             var_level, var_reason, decision_level):
    changed = True
    while changed:
        changed = False
        for clause_idx in range(len(row_ptr) - 1):
            start = row_ptr[clause_idx]
            end = row_ptr[clause_idx + 1]

            satisfied = False
            false_count = 0
            unit_lit = None

            for pos in range(start, end):
                var = col_indices[pos]
                pol = values[pos]

                if not assigned[var]:
                    unit_lit = int(pol) * (var + 1)
                else:
                    if assignment[var] == pol:
                        satisfied = True
                        break
                    else:
                        false_count += 1

            if satisfied:
                continue

            clause_len = end - start
            if false_count == clause_len:
                return clause_idx

            if false_count == clause_len - 1 and unit_lit is not None:
                uvar = abs(unit_lit) - 1
                if not assigned[uvar]:
                    logger.debug(f"BCP forced literal: {unit_lit} (reason clause {clause_idx})")
                    _assign(unit_lit, decision_level, clause_idx,
                            assignment, assigned, trail, var_level, var_reason)
                    changed = True

    return None


# 1-UIP conflict analysis - resolves back through the trail until one literal remains at the current level
def analyze_conflict(conflict_clause_idx, trail, trail_lim, var_level, var_reason,
                     values, col_indices, row_ptr, decision_level):
    in_clause = set()
    working = set()

    def add_literals(clause_idx):
        start = row_ptr[clause_idx]
        end = row_ptr[clause_idx + 1]
        for pos in range(start, end):
            var = col_indices[pos]
            pol = values[pos]
            if var not in working:
                working.add(var)
                in_clause.add((var, int(pol)))

    add_literals(conflict_clause_idx)

    trail_idx = len(trail) - 1
    while True:
        current_level_vars = [v for v in working if var_level[v] == decision_level]
        if len(current_level_vars) == 1:
            break

        while trail_idx >= 0:
            lit, lvl, _ = trail[trail_idx]
            var = abs(lit) - 1
            if lvl == decision_level and var in working:
                break
            trail_idx -= 1

        if trail_idx < 0:
            break

        resolve_var = abs(trail[trail_idx][0]) - 1
        reason_idx = var_reason[resolve_var]

        working.discard(resolve_var)
        in_clause = {(v, p) for v, p in in_clause if v != resolve_var}

        if reason_idx is not None:
            r_start = row_ptr[reason_idx]
            r_end = row_ptr[reason_idx + 1]
            for pos in range(r_start, r_end):
                var = col_indices[pos]
                pol = values[pos]
                if var != resolve_var and var not in working:
                    working.add(var)
                    in_clause.add((var, int(pol)))

        trail_idx -= 1

    # Negate the clause literals to form the learned clause
    learned_clause = [int(-pol) * (var + 1) for var, pol in in_clause]

    levels = sorted({var_level[var] for var, _ in in_clause if var_level[var] >= 0}, reverse=True)
    backjump_lvl = levels[1] if len(levels) > 1 else 0

    return learned_clause, backjump_lvl


# Undo all assignments above backjump_lvl
def backjump(backjump_lvl, assignment, assigned, trail, trail_lim, var_level, var_reason):
    target = trail_lim[backjump_lvl] if backjump_lvl < len(trail_lim) else 0

    while len(trail) > target:
        lit, _, _ = trail.pop()
        var = abs(lit) - 1
        assignment[var] = 0
        assigned[var] = False
        var_level[var] = -1
        var_reason[var] = None

    del trail_lim[backjump_lvl + 1:]


def add_learned_clause(values, col_indices, row_ptr, learned_clause):
    new_vals = np.array([1 if l > 0 else -1 for l in learned_clause], dtype=np.int8)
    new_cols = np.array([abs(l) - 1 for l in learned_clause], dtype=np.int32)
    new_row_ptr = np.append(row_ptr, row_ptr[-1] + len(learned_clause))
    return (
        np.concatenate([values, new_vals]),
        np.concatenate([col_indices, new_cols]),
        new_row_ptr,
    )


def _find_uip_in_learned(learned_clause, assigned):
    for lit in learned_clause:
        if not assigned[abs(lit) - 1]:
            return lit
    return None


def _assign(literal, decision_level, reason_clause_idx, assignment, assigned, trail, var_level, var_reason):
    var = abs(literal) - 1
    pol = 1 if literal > 0 else -1
    assignment[var] = pol
    assigned[var] = True
    var_level[var] = decision_level
    var_reason[var] = reason_clause_idx
    trail.append((literal, decision_level, reason_clause_idx))


def pick_literal(values, col_indices, assignment, assigned, num_vars):
    unassigned_mask = ~assigned[col_indices]
    unassigned_vals = values[unassigned_mask]
    unassigned_cols = col_indices[unassigned_mask]

    if len(unassigned_cols) == 0:
        return None

    pos_counts, neg_counts = dpll.get_literal_counts(unassigned_vals, unassigned_cols, num_vars)

    if not np.any(pos_counts + neg_counts):
        return None

    return dpll.select_literal(pos_counts, neg_counts)


def _build_result(assignment, num_vars):
    result = []
    for var in range(num_vars):
        if assignment[var] == 1:
            result.append(var + 1)
        elif assignment[var] == -1:
            result.append(-(var + 1))
    return result


if __name__ == "__main__":
    print("Not meant to be run directly. Please use 'main.py' to execute the program.")
