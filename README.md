# Directory Structure

## ```/code```

Contains all code.

```benchmark.py``` Contains benchmarking tools. No longer used in any way with the solver.\
```dimacs_parser.py``` Uses the CNF parser in the python-sat package in a wrapper function.\
```dpll.py``` Contains the DPLL algorithm and its helper functions.\
```globals.py``` Initializes input arguments parser variable as a global variable.\
```main.py``` Contains main function which handles command line function call input argument parsing, CNF parser, and starts DPLL.\
```moms.py``` Contains Maximum Occurrences in clauses of Minimum Size decision heuristic.\
```mySAT.py``` Top-level interface for the code.\
```requirements.txt``` Lists required python dependencies.

## ```/prob```
Contains conjunctive normal form (CNF) problem sets from [SATLIB](https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html)

```/uniform-random-3-sat``` 20 variables, 91 clauses - 1000 instances, all satisfiable
```/dubois``` Randomly generated SAT instances - 13 instances, all unsatisfiable
```/jnh``` Random SAT instances with variable length clauses - 16 instances satisfiable, 34 instances unsatisfiable

These problems were used for testing and benchmarking. We wrote two simple CNF problems,
```
3_input_and.cnf
unsat.cnf
```
to test functionality of the solver.

# Prerequisites
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r code/requirements.txt
```
No compilation necessary.

# How to run
## Linux
```
cd code
python3 mySAT.py {input_file}
```
