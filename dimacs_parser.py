from pysat.formula import CNF

def dimacs_parser(filepath):
    # Automatically parses the DIMACS CNF file
    cnf = CNF(from_file=filepath)

    print(f"Number of variables: {cnf.nv}")
    print(f"Number of clauses: {len(cnf.clauses)}")
    print(f"Clauses: {cnf.clauses}")

    return cnf

# def print_parsed_data(parsed_cnf):
    # Access the parsed data

user_input = input("Filepath: ")
dimacs_parser(user_input)

