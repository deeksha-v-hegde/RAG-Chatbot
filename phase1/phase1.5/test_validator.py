"""
Automated Unit Tests for Phase 1.5: Ingestion Validation & Integrity Verification
Module: test_validator.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from validator import IngestionValidator


class TestIngestionValidator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.validator = IngestionValidator()
        cls.report = cls.validator.validate_corpus()

    def test_overall_audit_passed(self):
        self.assertEqual(
            self.report["status"],
            "PASSED",
            f"Audit failed with errors: {self.report['summary_errors']}",
        )
        self.assertTrue(self.report["all_checks_passed"])
        self.assertEqual(len(self.report["summary_errors"]), 0)

    def test_report_file_created(self):
        self.assertTrue(self.validator.report_file.exists())
        self.assertGreater(self.validator.report_file.stat().st_size, 500)

    def test_all_schemes_passed_individual_assertions(self):
        self.assertEqual(len(self.report["schemes"]), 5)
        for scheme_rep in self.report["schemes"]:
            self.assertEqual(
                scheme_rep["status"],
                "PASS",
                f"Scheme {scheme_rep['scheme_id']} failed: {scheme_rep['errors']}",
            )
            self.assertGreaterEqual(scheme_rep["checks_passed_count"], 7)


if __name__ == "__main__":
    unittest.main()
