"""
Local Scheduler & Corpus Freshness Runner
Simulates the GitHub Actions automated data freshness workflow locally.

Usage:
    python run_scheduler_local.py                # Run once immediately
    python run_scheduler_local.py --interval 60  # Run recurringly every 60 minutes
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

PROJECT_ROOT = Path(__file__).resolve().parent

def run_step(step_name: str, command: list[str]) -> bool:
    """Executes a single workflow step and logs results."""
    print(f"\n========================================================")
    print(f">> [STEP] {step_name}")
    print(f"   Command: {' '.join(command)}")
    print(f"========================================================")
    start_time = time.time()
    try:
        res = subprocess.run(
            [sys.executable] + command[1:],
            cwd=str(PROJECT_ROOT),
            check=True,
            text=True,
        )
        elapsed = time.time() - start_time
        print(f"[OK] {step_name} completed successfully in {elapsed:.2f}s")
        return True
    except subprocess.CalledProcessError as err:
        elapsed = time.time() - start_time
        print(f"[FAILED] {step_name} failed with exit code {err.returncode} ({elapsed:.2f}s)")
        return False


def execute_data_freshness_pipeline() -> bool:
    """Runs the complete data freshness and re-indexing pipeline."""
    pipeline_start = time.time()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n########################################################")
    print(f"# Starting Automated Data Freshness Pipeline ({now_str})")
    print(f"########################################################")

    # Step 1: Force-refresh raw Groww scheme disclosures
    s1 = run_step(
        "1. Ingestion Pipeline (Scrape & Normalize 5 Schemes)",
        ["python", "phase1/run_ingestion.py", "--force-refresh"]
    )
    if not s1:
        return False

    # Step 2: Rebuild Vector Index & Chunk Embeddings
    s2 = run_step(
        "2. Indexing Pipeline (Chunk & Vectorize)",
        ["python", "phase2/run_phase2.py", "--build-index"]
    )
    if not s2:
        return False

    # Step 3: Run Verification Smoke Tests
    s3_reg = run_step("3a. Registry Verification Test", ["python", "phase1/phase1.1/test_registry.py"])
    s3_idx = run_step("3b. Indexer Verification Test", ["python", "phase2/test_indexer.py"])
    s3_ret = run_step("3c. Retriever Verification Test", ["python", "phase2/test_retriever.py"])

    if not (s3_reg and s3_idx and s3_ret):
        print("\n[FAILED] Smoke tests failed. Halting pipeline.")
        return False

    # Step 4: Check Diff
    print(f"\n========================================================")
    print(f">> [STEP] 4. Evaluating Corpus Diff")
    print(f"========================================================")
    try:
        diff_res = subprocess.run(
            ["git", "status", "-s", "data/"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )
        diff_output = diff_res.stdout.strip()
        if diff_output:
            print(f"[DIFF] Changes detected in corpus / index:\n{diff_output}")
        else:
            print("[OK] No changes in disclosures. Corpus is up to date.")
    except Exception as e:
        print(f"Note: git diff check skipped ({e})")

    total_time = time.time() - pipeline_start
    print(f"\n########################################################")
    print(f"[SUCCESS] Pipeline successfully completed in {total_time:.2f}s!")
    print(f"########################################################\n")
    return True


def main():
    parser = argparse.ArgumentParser(description="Local Data Freshness Scheduler")
    parser.add_argument(
        "--interval",
        type=int,
        default=0,
        help="Recurring schedule interval in minutes (default: 0 = run once).",
    )
    args = parser.parse_args()

    if args.interval <= 0:
        success = execute_data_freshness_pipeline()
        sys.exit(0 if success else 1)
    else:
        print(f"Starting recurring scheduler every {args.interval} minutes. Press Ctrl+C to stop.")
        while True:
            execute_data_freshness_pipeline()
            print(f"Sleeping for {args.interval} minutes until next scheduled run...")
            time.sleep(args.interval * 60)


if __name__ == "__main__":
    main()
