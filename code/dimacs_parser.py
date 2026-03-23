#!/usr/bin/env python

from pysat.formula import CNF

def dimacs_parser(filepath):
    # 1. Read and filter the file content
    clean_lines = []
    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()
            # Stop reading if we hit the legacy EOF marker '%'
            if stripped == "%":
                break

            # Skip empty lines or the very last trailing '0'
            # (Note: Clause-terminating 0s stay because they are part of the clause lines)
            if not stripped:
                continue

            clean_lines.append(line)

    # 2. Join the clean lines into a single string
    clean_content = "".join(clean_lines)

    # 3. Parse from string instead of file path
    cnf = CNF(from_string=clean_content)

    return cnf

def print_parsed_data(parsed_cnf):
    print(f"Number of variables: {parsed_cnf.nv}")
    print(f"Number of clauses: {len(parsed_cnf.clauses)}")

    for idx, clause in enumerate(parsed_cnf.clauses):
        print(f"Clause {idx}: {clause}")

if __name__ == "__main__":
    user_input = input("Filepath: ")
    cnf = dimacs_parser(user_input)
    print_parsed_data(cnf)