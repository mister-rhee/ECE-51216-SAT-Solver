import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input CNF path. Can be relative or absolute path", type=str)
    args = parser.parse_args()

    subprocess.run(["python3", "main.py", "-m", args.input])