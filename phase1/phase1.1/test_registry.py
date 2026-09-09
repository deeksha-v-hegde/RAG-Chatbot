"""
Automated Unit Tests for Phase 1.1: Sources Whitelist Registry
Module: test_registry.py
"""

import sys
import unittest
from pathlib import Path

# Ensure local module import works regardless of current working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))

from registry import SchemeRegistry, SchemeSource, WHITELISTED_URLS


class TestSchemeRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = SchemeRegistry()

    def test_exact_five_schemes_registered(self):
        schemes = self.registry.get_all()
        self.assertEqual(len(schemes), 5, "Expected exactly 5 registered schemes.")

    def test_all_urls_are_in_whitelist(self):
        for scheme in self.registry.get_all():
            self.assertIn(
                scheme.source_url,
                WHITELISTED_URLS,
                f"URL {scheme.source_url} must be in the approved whitelist.",
            )

    def test_unapproved_url_is_rejected(self):
        unapproved_url = "https://groww.in/mutual-funds/sbi-small-cap-fund-direct-growth"
        self.assertFalse(self.registry.is_url_allowed(unapproved_url))

        with self.assertRaises(ValueError):
            bad_scheme = SchemeSource(
                scheme_id="sbi_small_cap",
                canonical_name="SBI Small Cap Fund",
                plan_type="Direct - Growth",
                category="Small Cap",
                source_url=unapproved_url,
                citation_title="Groww SBI",
                expected_metrics=["expense_ratio"],
            )
            bad_scheme.validate()

    def test_elss_statutory_lock_in_years(self):
        elss_scheme = self.registry.get_by_id("hdfc_elss")
        self.assertIsNotNone(elss_scheme)
        self.assertEqual(elss_scheme.statutory_lock_in_years, 3)

    def test_alias_resolution(self):
        test_queries = [
            ("What is the expense ratio for HDFC Mid Cap?", "hdfc_mid_cap"),
            ("Tell me the exit load of HDFC Flexicap", "hdfc_flexi_cap"),
            ("What is the lock-in for HDFC tax saver?", "hdfc_elss"),
            ("HDFC Top 100 riskometer classification", "hdfc_large_cap"),
            ("Minimum SIP amount in HDFC focused 30", "hdfc_focused"),
        ]
        for query, expected_id in test_queries:
            matched = self.registry.resolve_scheme_from_query(query)
            self.assertIsNotNone(matched, f"Failed to resolve scheme from query: '{query}'")
            self.assertEqual(matched.scheme_id, expected_id)

    def test_ambiguous_or_unspecified_query(self):
        # Query with no scheme specified should return None
        result = self.registry.resolve_scheme_from_query("What is the expense ratio?")
        self.assertIsNone(result)

        # Query with multiple schemes specified should return None (ambiguous)
        result = self.registry.resolve_scheme_from_query("Compare HDFC Mid Cap and HDFC Flexi Cap")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
