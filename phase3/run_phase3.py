"""
CLI Runner for Phase 3: Compliance Guardrails & Refusal Engine
Usage:
    python phase3/run_phase3.py --query "Should I invest in HDFC Mid Cap?"
    python phase3/run_phase3.py --query "What is the exit load for HDFC Mid Cap?"
"""

import sys
import argparse
from pathlib import Path

# Add search path for phase3
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from guardrails import ComplianceGuardrail


def main():
    parser = argparse.ArgumentParser(description="Phase 3: Compliance Guardrails & Refusal Engine")
    parser.add_argument("--query", type=str, required=True, help="User query to evaluate through guardrails.")

    args = parser.parse_args()

    print(f"\n>>> Evaluating Query: '{args.query}'")
    guard = ComplianceGuardrail()
    decision = guard.evaluate(args.query)

    print(f"Decision Status: {'[ALLOWED]' if decision.allowed_to_retrieve else '[BLOCKED / REFUSED]'}")
    print(f"Detected Intent: {decision.intent.value}")
    print(f"Reason: {decision.reason}")

    if decision.is_refusal:
        print("\n--- Structured Refusal Response ---")
        print(decision.refusal_response.full_markdown)
    else:
        print("\n[OK] Query cleared to proceed to Phase 2 Retrieval & Vector Search.")


if __name__ == "__main__":
    main()
