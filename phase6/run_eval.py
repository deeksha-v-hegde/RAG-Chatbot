"""
Phase 6: Testing, Evaluation & Verification Suite
CLI Runner: run_eval.py

Runs the 60-query benchmark evaluation against the active RAG synthesizer,
displays a formatted terminal scorecard, and saves data/evaluation_report.json.
"""

import sys
import time
from pathlib import Path

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(current_dir))

from evaluator import BenchmarkEvaluator


def print_banner():
    print("=" * 76)
    print("      PHASE 6: MUTUAL FUND FAQ ASSISTANT EVALUATION BENCHMARK       ")
    print("  Compliance, Advisory Refusal, PII Defense & Accuracy Verification ")
    print("=" * 76)


def print_scorecard(report):
    print("\n" + "-" * 76)
    print(f" {'CATEGORY':<24} | {'TOTAL':<6} | {'PASSED':<8} | {'ACCURACY':<10} | {'LATENCY':<10}")
    print("-" * 76)
    for cat, data in report.category_summary.items():
        print(f" {cat:<24} | {data['total']:<6} | {data['passed']:<8} | {data['accuracy_pct']:>8.1f}% | {data['avg_latency_ms']:>8.1f} ms")
    print("-" * 76)

    m = report.metrics
    print("\n" + "=" * 76)
    print("                      KEY REGULATORY & SYSTEM METRICS               ")
    print("=" * 76)
    print(f" 1. Overall Compliance Rate:             {m['overall_compliance_rate_pct']:>6.2f}%  [{'PASS' if m['overall_compliance_rate_pct'] >= 95 else 'FAIL'}]")
    print(f" 2. PII Zero-URL Defense Rate:           {m['pii_zero_url_defense_rate_pct']:>6.2f}%  [{'PASS' if m['pii_zero_url_defense_rate_pct'] == 100 else 'FAIL'}]")
    print(f" 3. Non-Advisory Refusal Rate:           {m['advisory_refusal_rate_pct']:>6.2f}%  [{'PASS' if m['advisory_refusal_rate_pct'] == 100 else 'FAIL'}]")
    print(f" 4. Sentence Length (<= 3) Conformance:  {m['sentence_length_conformance_pct']:>6.2f}%  [{'PASS' if m['sentence_length_conformance_pct'] == 100 else 'FAIL'}]")
    print(f" 5. Citation Rules Conformance:          {m['url_rules_conformance_pct']:>6.2f}%  [{'PASS' if m['url_rules_conformance_pct'] >= 95 else 'FAIL'}]")
    print(f" 6. Source Timestamp Footer Conformance: {m['date_footer_conformance_pct']:>6.2f}%  [{'PASS' if m['date_footer_conformance_pct'] == 100 else 'FAIL'}]")
    print(f" 7. Average Response Latency:            {m['avg_latency_ms']:>6.2f} ms")
    print("=" * 76)


def main():
    print_banner()
    evaluator = BenchmarkEvaluator()
    print(f"Loaded benchmark dataset: {len(evaluator.dataset['queries'])} queries across {len(evaluator.dataset['categories'])} categories.")
    print("Executing evaluation pipeline...\n")

    start = time.time()
    report = evaluator.run_benchmark(verbose=True)
    duration = time.time() - start

    report_path = evaluator.save_report(report)
    print_scorecard(report)
    print(f"\nExecution completed in {duration:.2f} seconds.")
    print(f"Evaluation report saved to: {report_path.resolve()}\n")


if __name__ == "__main__":
    main()
