from pysat.formula import CNF

# Automatically parses the DIMACS CNF file
cnf = CNF(from_file='uf20-91/uf20-01.cnf')

# Access the parsed data
print(f"Number of variables: {cnf.nv}")
print(f"Number of clauses: {len(cnf.clauses)}")
print(f"Clauses: {cnf.clauses}")