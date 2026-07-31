#!/usr/bin/env python3
"""
Evaluate the benchmarking dataset against the project's evaluation framework
(Objective 4).

Computes the four metrics defined in the dissertation:
  1. Deployment success rate (primary reliability indicator)
  2. Execution time (min / max / mean, cold starts separated from warm runs)
  3. Configuration footprint (files and lines needed to adopt the pipeline)
  4. Recovery time (time to return to a successful deployment after a failure)

The success-rate and recovery-time results are read from the recorded runs.
The configuration footprint is reported per application from the columns in
the dataset. Pre-set thresholds (fixed before the runs, per section 3.5) are
applied so the judgement rests on a standard that cannot be moved afterwards.

Usage:
    python3 evaluate.py docs/benchmark_dataset_template.csv
"""
import csv
import sys
from collections import defaultdict

# Pre-set evaluation thresholds (fixed in advance; see dissertation, 3.5).
STRONG_SUCCESS_RATE = 95.0        # at or above: strong reliability
ACCEPTABLE_SUCCESS_RATE = 80.0    # 80–95%: acceptable with caveats; below: not dependable

SUCCESS_VALUES = ("1", "true", "yes", "success")


def is_success(value):
    return value.strip().lower() in SUCCESS_VALUES


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def evaluate(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # Skip rows that have not been filled in yet.
            if row.get("deployment_success", "").strip():
                rows.append(row)

    if not rows:
        print("No completed runs in the dataset. Run the pipeline first, then "
              "append the recorded metrics.")
        return

    by_app = defaultdict(list)
    for row in rows:
        by_app[row["application"]].append(row)

    print("=" * 64)
    print("PIPELINE EVALUATION REPORT")
    print("=" * 64)

    total_success = 0
    total_runs = 0
    all_recoveries = []

    for app, app_rows in by_app.items():
        runs = len(app_rows)
        successes = sum(1 for r in app_rows if is_success(r["deployment_success"]))

        # Separate cold-start runs from warm runs so the host's sleep behaviour
        # is visible rather than hidden (see 3.5).
        cold_times, warm_times = [], []
        for r in app_rows:
            t = as_float(r.get("execution_time_seconds", ""))
            if t is None:
                continue
            if is_success(r.get("cold_start", "")):
                cold_times.append(t)
            else:
                warm_times.append(t)

        # Recovery time is recorded only on runs that follow a failure.
        recoveries = [
            as_float(r.get("recovery_time_seconds", ""))
            for r in app_rows
            if as_float(r.get("recovery_time_seconds", "")) is not None
        ]
        all_recoveries.extend(recoveries)

        total_success += successes
        total_runs += runs

        rate = (successes / runs * 100) if runs else 0
        print(f"\nApplication: {app}")
        print(f"  Runs                         : {runs}")
        print(f"  Deployment success rate      : {rate:.1f}% ({successes}/{runs})")

        all_times = warm_times + cold_times
        if all_times:
            print(f"  Execution time (all runs)    : "
                  f"min {min(all_times):.1f}s / max {max(all_times):.1f}s / "
                  f"mean {sum(all_times) / len(all_times):.1f}s")
        if warm_times:
            print(f"  Execution time (warm runs)   : "
                  f"mean {sum(warm_times) / len(warm_times):.1f}s over {len(warm_times)} run(s)")
        if cold_times:
            print(f"  Execution time (cold starts) : "
                  f"mean {sum(cold_times) / len(cold_times):.1f}s over {len(cold_times)} run(s)")

        # Configuration footprint per application, read from the dataset.
        files = next((r.get("config_files", "").strip() for r in app_rows
                      if r.get("config_files", "").strip()), "")
        lines = next((r.get("config_lines", "").strip() for r in app_rows
                      if r.get("config_lines", "").strip()), "")
        if files or lines:
            print(f"  Configuration footprint      : {files} file(s), {lines} line(s)")

        if recoveries:
            print(f"  Recovery time                : "
                  f"{len(recoveries)} recovery(ies), "
                  f"mean {sum(recoveries) / len(recoveries):.1f}s")

    print("\n" + "-" * 64)
    overall_rate = (total_success / total_runs * 100) if total_runs else 0
    print("OVERALL RESULTS")
    print(f"  Total runs                   : {total_runs}")
    print(f"  Overall success rate         : {overall_rate:.1f}%")

    # Apply the pre-set reliability thresholds.
    if overall_rate >= STRONG_SUCCESS_RATE:
        verdict = "STRONG (>= 95%)"
    elif overall_rate >= ACCEPTABLE_SUCCESS_RATE:
        verdict = "ACCEPTABLE WITH CAVEATS (80-95%)"
    else:
        verdict = "NOT YET DEPENDABLE (< 80%)"
    print(f"  Reliability verdict          : {verdict}")

    if all_recoveries:
        print(f"  Recovery time (all)          : "
              f"{len(all_recoveries)} recovery(ies), "
              f"mean {sum(all_recoveries) / len(all_recoveries):.1f}s")
    else:
        print("  Recovery time (all)          : no failures recorded in the "
              "natural runs; measure recovery via the controlled fault "
              "scenarios (workflow_dispatch -> fault_scenario).")
    print("-" * 64)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 evaluate.py <dataset.csv>")
        sys.exit(1)
    evaluate(sys.argv[1])
