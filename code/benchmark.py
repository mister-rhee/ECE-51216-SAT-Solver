#!/usr/bin/env python3

import os
import subprocess
import time
import csv
import matplotlib.pyplot as plt
import logging

# Configuration
INPUT_DIR = "prob/uniform-random-3-sat"
SOLVER = "code/main.py"
RESULTS_DIR = "results"
OUTPUT_CHART = "results/benchmark_results.png"
OUTPUT_CSV = "results/benchmark_data.csv"

def run_benchmarks():
    # Ensure the results directory exists so we don't crash on save
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
        logging.info(f"Created directory: {RESULTS_DIR}")

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.cnf')]
    results = []

    print(f"{'File':<30} | {'Status':<10} | {'Time (s)':<10}")
    print("-" * 55)

    for cnf_file in files:
        file_path = os.path.join(INPUT_DIR, cnf_file)

        start_time = time.perf_counter()
        try:
            process = subprocess.run(
                ["python", SOLVER, file_path],
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

    # Save the data and then visualize it
    save_to_csv(results)
    generate_histogram(results)

def save_to_csv(results):
    """Writes the benchmark results to a CSV file."""
    keys = results[0].keys() if results else ["name", "time", "status"]

    try:
        with open(OUTPUT_CSV, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"\nData successfully saved to: {OUTPUT_CSV}")
    except IOError as e:
        logging.error(f"Failed to write CSV: {e}")

def generate_histogram(results):
    # Separate successful runs from failures
    success_times = [r['time'] for r in results if r['status'] in ["SAT", "UNSAT"]]
    failed_names = [r['name'] for r in results if r['status'] not in ["SAT", "UNSAT"]]

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
    plt.savefig(OUTPUT_CHART)
    print(f"Chart saved to: {OUTPUT_CHART}")
    if failed_names:
        print(f"Total failures: {len(failed_names)}")

if __name__ == "__main__":
    run_benchmarks()