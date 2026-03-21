from pysat.formula import CNF

def dimacs_parser(filepath):
    # Automatically parses the DIMACS CNF file
    cnf = CNF(from_file=filepath)

    return cnf

def print_parsed_data(parsed_cnf):
    # Access the parsed data
    print(f"Number of variables: {parsed_cnf.nv}")
    print(f"Number of clauses: {len(parsed_cnf.clauses)}")
    print(f"Clauses: {parsed_cnf.clauses}")