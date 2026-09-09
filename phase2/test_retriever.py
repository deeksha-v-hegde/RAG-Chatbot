"""
Automated Unit Tests for Phase 2: Scheme Retriever
Module: test_retriever.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))

from retriever import SchemeRetriever, RetrievalResult
from registry import WHITELISTED_URLS


class TestSchemeRetriever(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.retriever = SchemeRetriever()

    def test_exact_scheme_and_metric_retrieval(self):
        test_cases = [
            ("What is the exit load for HDFC Mid Cap?", "hdfc_mid_cap_exit_load"),
            ("Tell me the expense ratio of HDFC Flexicap", "hdfc_flexi_cap_ter"),
            ("What is the lock in period for HDFC ELSS Tax Saver?", "hdfc_elss_lock_in"),
            ("Minimum SIP amount in HDFC Top 100", "hdfc_large_cap_investment_limits"),
            ("What is the riskometer rating of HDFC Focused 30?", "hdfc_focused_risk_benchmark"),
        ]

        for query, expected_chunk_id in test_cases:
            res = self.retriever.retrieve(query, top_k=1)
            self.assertEqual(res.status_message, "SUCCESS", f"Failed on query: {query}")
            self.assertIsNotNone(res.top_chunk, f"No top chunk for: {query}")
            self.assertEqual(
                res.top_chunk["chunk_id"],
                expected_chunk_id,
                f"Expected chunk '{expected_chunk_id}', got '{res.top_chunk['chunk_id']}' for query '{query}'",
            )
            self.assertIn(res.top_chunk["source_url"], WHITELISTED_URLS)
            self.assertGreater(res.top_score, 0.1)

    def test_disambiguation_when_scheme_unspecified(self):
        queries = [
            "What is the exit load?",
            "Tell me the expense ratio",
            "What is the minimum SIP?",
        ]
        for q in queries:
            res = self.retriever.retrieve(q)
            self.assertTrue(
                res.is_disambiguation,
                f"Query '{q}' should trigger disambiguation prompt because no scheme is specified.",
            )
            self.assertIn("specify which HDFC fund", res.status_message)

    def test_unsupported_foreign_scheme_detected(self):
        queries = [
            "What is the expense ratio of SBI Bluechip?",
            "What is the exit load of ICICI Prudential Technology Fund?",
            "Tell me about Axis Midcap Fund",
        ]
        for q in queries:
            res = self.retriever.retrieve(q)
            self.assertTrue(
                res.is_unsupported_scheme,
                f"Query '{q}' should trigger out-of-corpus boundary warning.",
            )
            self.assertIn("Out of Scope", res.status_message)


if __name__ == "__main__":
    unittest.main()
