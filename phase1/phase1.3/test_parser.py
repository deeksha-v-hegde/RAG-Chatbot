"""
Automated Unit Tests for Phase 1.3: DOM Parsing, Semantic Section Extraction & Sanitization
Module: test_parser.py
"""

import sys
import unittest
from pathlib import Path

# Add search path for parser module
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from parser import SchemeDOMParser, ParsedSchemeData


class TestSchemeDOMParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.parser = SchemeDOMParser()
        cls.parsed_schemes = cls.parser.parse_all()

    def test_all_five_schemes_parsed(self):
        expected_ids = {
            "hdfc_mid_cap",
            "hdfc_flexi_cap",
            "hdfc_focused",
            "hdfc_elss",
            "hdfc_large_cap",
        }
        self.assertEqual(set(self.parsed_schemes.keys()), expected_ids)

    def test_expense_ratios(self):
        for sid, data in self.parsed_schemes.items():
            self.assertGreater(data.expense_ratio_val, 0.0, f"TER should be > 0 for {sid}")
            self.assertTrue(data.expense_ratio.endswith("%"), f"TER string must end with % for {sid}")

    def test_exit_load_extracted(self):
        for sid, data in self.parsed_schemes.items():
            self.assertTrue(len(data.exit_load) > 0, f"Exit load must not be empty for {sid}")
            if sid == "hdfc_elss":
                self.assertEqual(data.exit_load, "Nil", "ELSS exit load is nil")
            else:
                self.assertIn("1%", data.exit_load, f"Expected 1% in exit load for equity fund {sid}")

    def test_minimum_investments(self):
        for sid, data in self.parsed_schemes.items():
            self.assertGreaterEqual(data.min_sip_val, 100, f"Min SIP must be >= 100 for {sid}")
            self.assertTrue(data.min_sip.startswith("₹"), f"Min SIP string must start with ₹ for {sid}")

        # ELSS minimum is typically ₹500
        elss_data = self.parsed_schemes["hdfc_elss"]
        self.assertEqual(elss_data.min_sip_val, 500, "HDFC ELSS Min SIP should be ₹500")

    def test_riskometer_and_benchmark(self):
        for sid, data in self.parsed_schemes.items():
            self.assertTrue(len(data.riskometer) > 0, f"Riskometer must be present for {sid}")
            self.assertTrue(len(data.benchmark) > 0, f"Benchmark must be present for {sid}")
            self.assertIn("NIFTY", data.benchmark, f"Benchmark should contain NIFTY for HDFC funds {sid}")

    def test_elss_statutory_lock_in(self):
        elss_data = self.parsed_schemes["hdfc_elss"]
        self.assertEqual(elss_data.lock_in_years, 3, "HDFC ELSS must have 3-year statutory lock-in")
        self.assertIn("3 Years", elss_data.lock_in)

        # Other equity funds have no lock-in
        midcap_data = self.parsed_schemes["hdfc_mid_cap"]
        self.assertIsNone(midcap_data.lock_in_years, "Mid Cap fund should not have statutory lock-in years")
        self.assertIn("Nil", midcap_data.lock_in)


if __name__ == "__main__":
    unittest.main()
