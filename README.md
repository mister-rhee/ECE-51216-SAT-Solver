# Directory Structure

```/code``` contains all code.\
```/prob``` contains three directories

```
/dimacs
/dubois
/jnh
```
which we used for testing and benchmarking, and two files
```
3_input_and.cnf
unsat.cnf
```
which we created for testing functionality.

# Prerequisites
No compilation necessary.

# How to run
## Linux
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r code/requirements.txt
cd code
python3 mySAT.py {input_file}
```
