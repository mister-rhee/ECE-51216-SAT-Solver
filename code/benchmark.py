#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import csv
import matplotlib.pyplot as plt
import logging

# Configuration
INPUT_DIR = "prob"
PROBLEM_SETS = [os.path.join(INPUT_DIR, d) for d in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, d))]

SOLVER = "code/main.py"
OPTIONS = ['', '-m', '-c', '-mc']

RESULTS_DIR = "results"

def map_option_to_str(option):
    if option == "-m":
        return "moms"
    elif option == "-c":
        return "cdcl"
    elif option == "-mc":
        return "full"
    else:
        return "none"

def run_benchmarks(problem_set_path, option):
    problem_set_basename = os.path.basename(problem_set_path)

    result_path = os.path.join(RESULTS_DIR, problem_set_basename)

    # Ensure the results directory exists so we don't crash on save
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        logging.info(f"Created directory: {RESULTS_DIR}")

    if not os.path.exists(result_path):
        os.makedirs(result_path)
        logging.info(f"Created directory: {result_path}")

    files = [f for f in os.listdir(problem_set_path) if f.endswith('.cnf')]
    results = []

    print(f"{'File':<30} | {'Status':<10} | {'Time (s)':<10}")
    print("-" * 55)

    for cnf_file in files:
        file_path = os.path.join(problem_set_path, cnf_file)

        cmd = [sys.executable, SOLVER]
        if option:
            cmd.append(option)
        cmd.append(file_path)

        start_time = time.perf_counter()

        try:
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            duration = time.perf_counter() - start_time

            if process.returncode == 0:
                status = "SAT"
            elif process.returncode == 1:
                status = "UNSAT"
            else:
                status = "FAILED"
                logging.error(f"Error in {cnf_file}: {process.stderr}")

        except subprocess.TimeoutExpired:
            duration = 60.0
            status = "TIMEOUT"
        except Exception as e:
            duration = 0.0
            status = f"ERROR: {str(e)}"

        results.append({
            "name": cnf_file,
            "time": duration,
            "status": status
        })

        print(f"{cnf_file[:30]:<30} | {status:<10} | {duration:<10.4f}")

    option_string = map_option_to_str(option)

    # Save the data and then visualize it
    save_to_csv(results, result_path, option_string)
    generate_histogram(results, result_path, option_string)

def save_to_csv(results, result_path, option):
    """Writes the benchmark results to a CSV file."""
    keys = results[0].keys() if results else ["name", "time", "status"]

    csv_output = os.path.join(result_path, f'benchmark_{option}.csv')

    try:
        with open(csv_output, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"\nData successfully saved to: {csv_output}")
    except IOError as e:
        logging.error(f"Failed to write CSV: {e}")

def generate_histogram(results, result_path, option):
    # Separate successful runs from failures
    success_times = [r['time'] for r in results if r['status'] in ["SAT", "UNSAT"]]
    failed_names = [r['name'] for r in results if r['status'] not in ["SAT", "UNSAT"]]

    plt_output = os.path.join(result_path, f'benchmark_{option}.png')

    if not success_times:
        print("No successful runs (SAT/UNSAT) to plot.")
        return

    plt.figure(figsize=(10, 6))

    # Create the histogram
    plt.hist(success_times, bins=20, color='skyblue', edgecolor='black', alpha=0.7)

    plt.title('Distribution of SAT Solver Run-times', fontsize=14)
    plt.xlabel('Execution Time (seconds)', fontsize=12)
    plt.ylabel('Number of CNF Files', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add a text box for failures so you can glean them quickly
    if failed_names:
        fail_text = "Failures/Timeouts:\n" + "\n".join(failed_names[:5])
        if len(failed_names) > 5:
            fail_text += "\n..."
        plt.text(0.95, 0.95, fail_text, transform=plt.gca().transAxes,
                 verticalalignment='top', horizontalalignment='right',
                 bbox=dict(boxstyle='round', facecolor='red', alpha=0.2))

    plt.tight_layout()
    plt.savefig(plt_output)
    print(f"Chart saved to: {plt_output}")
    if failed_names:
        print(f"Total failures: {len(failed_names)}")

if __name__ == "__main__":
    for prob in PROBLEM_SETS:
        for opt in OPTIONS:
            run_benchmarks(prob, opt)