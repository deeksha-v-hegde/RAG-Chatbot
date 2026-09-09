"""
Phase 4: RAG Prompting & Output Synthesis
CLI Runner: run_phase4.py

Provides an interactive and batch test interface for querying the Phase 4 RAG pipeline.
"""

import sys
import argparse
from pathlib import Path

# Ensure utf-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))
sys.path.insert(0, str(project_root / "phase2"))
sys.path.insert(0, str(project_root / "phase3"))
sys.path.insert(0, str(current_dir))

from synthesizer import RAGSynthesizer


DEMO_QUERIES = [
    ("Factual - Exit Load", "What is the exit load for HDFC Mid-Cap Opportunities Fund?"),
    ("Factual - Expense Ratio", "What is the expense ratio of HDFC Flexicap Direct Plan?"),
    ("Factual - Lock-in Period", "Does HDFC ELSS Tax Saver have a lock-in period?"),
    ("Factual - Minimum SIP", "What is the minimum SIP amount for HDFC Focused 30?"),
    ("Advisory Refusal", "Should I invest in HDFC Top 100 for high returns?"),
    ("Comparison Refusal", "Which is better between HDFC Mid Cap and HDFC Flexi Cap?"),
    ("PII Interception", "My PAN number is ABCDE1234F, can you show my investment statement?"),
    ("Missing Scheme Disambiguation", "What is the exit load?"),
    ("Out-of-Scope Foreign AMC", "What is the expense ratio for SBI Small Cap Fund?"),
]


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def format_response(resp):
    print(f"Status: {'REFUSAL' if resp.is_refusal else 'DISAMBIGUATION' if resp.is_disambiguation else 'ANSWER'}")
    print(f"Model / Engine: {resp.model_used}")
    print(f"Sentences: {resp.sentence_count} (Limit <= 3)")
    print(f"Citations attached: {resp.url_count}")
    if resp.source_url:
        print(f"Source URL: {resp.source_url}")
    print("-" * 70)
    print(resp.markdown_output)
    print("-" * 70)


def run_demo(synthesizer: RAGSynthesizer):
    print_header("PHASE 4: DEMO QUERY SUITE")
    print(f"Running {len(DEMO_QUERIES)} diverse compliance and factual test cases...\n")

    for idx, (label, query) in enumerate(DEMO_QUERIES, 1):
        print(f"\n[{idx}/{len(DEMO_QUERIES)}] Category: {label}")
        print(f"User Query: \"{query}\"")
        resp = synthesizer.answer_query(query)
        format_response(resp)


def run_interactive(synthesizer: RAGSynthesizer):
    print_header("PHASE 4: INTERACTIVE FAQ ASSISTANT")
    print("Ask any question about the 5 designated HDFC Mutual Fund schemes on Groww.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("\nEnter Question: ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                print("Exiting Phase 4 Assistant. Goodbye!")
                break

            resp = synthesizer.answer_query(query)
            print()
            format_response(resp)

        except KeyboardInterrupt:
            print("\nExiting.")
            break


def main():
    parser = argparse.ArgumentParser(description="Phase 4: RAG Prompting & Synthesis Runner")
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive chat mode")
    parser.add_argument("--query", "-q", type=str, help="Submit a single query directly")
    args = parser.parse_args()

    synthesizer = RAGSynthesizer()

    if args.query:
        print_header("SINGLE QUERY EXECUTION")
        print(f"User Query: \"{args.query}\"")
        resp = synthesizer.answer_query(args.query)
        format_response(resp)
    elif args.interactive:
        run_interactive(synthesizer)
    else:
        run_demo(synthesizer)


if __name__ == "__main__":
    main()
