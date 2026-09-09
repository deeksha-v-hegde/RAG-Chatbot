"""
Automated Unit Tests for Phase 1.4: Normalized Document Generation & Metadata Tagging
Module: test_normalizer.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent / "phase1.1"))
sys.path.insert(0, str(current_dir.parent / "phase1.3"))

from normalizer import SchemeNormalizer, NormalizedSchemeDocument
from registry import WHITELISTED_URLS


class TestSchemeNormalizer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.normalizer = SchemeNormalizer()
        cls.normalized_docs = cls.normalizer.normalize_all()

    def test_all_five_schemes_normalized(self):
        expected_ids = {
            "hdfc_mid_cap",
            "hdfc_flexi_cap",
            "hdfc_focused",
            "hdfc_elss",
            "hdfc_large_cap",
        }
        self.assertEqual(set(self.normalized_docs.keys()), expected_ids)

        # Check physical output files exist
        for sid in expected_ids:
            json_file = self.normalizer.processed_dir / f"{sid}.json"
            md_file = self.normalizer.processed_dir / f"{sid}.md"
            self.assertTrue(json_file.exists(), f"Missing processed JSON for {sid}")
            self.assertTrue(md_file.exists(), f"Missing processed Markdown for {sid}")

    def test_metadata_attributes_and_whitelist(self):
        for sid, doc in self.normalized_docs.items():
            self.assertIn(doc.source_url, WHITELISTED_URLS, f"Invalid URL for {sid}")
            self.assertTrue(len(doc.citation_label) > 0)
            self.assertEqual(doc.doc_type, "Scheme Overview")
            self.assertEqual(doc.last_updated, "2026-09-09")
            self.assertIn("expense_ratio", doc.sections)
            self.assertIn("exit_load", doc.sections)
            self.assertIn("min_sip", doc.sections)
            self.assertIn("riskometer", doc.sections)
            self.assertIn("benchmark", doc.sections)

    def test_structured_chunks_presence(self):
        expected_topics = {
            "expense_ratio",
            "exit_load",
            "investment_limits",
            "riskometer_and_benchmark",
            "lock_in_period",
            "overview_and_tax",
        }
        for sid, doc in self.normalized_docs.items():
            self.assertGreaterEqual(len(doc.structured_chunks), 6)
            doc_topics = {c["topic"] for c in doc.structured_chunks}
            self.assertEqual(expected_topics, doc_topics, f"Mismatch in topics for {sid}")

            # Verify chunk prefix injection
            for chunk in doc.structured_chunks:
                self.assertTrue(
                    chunk["text"].startswith("[Scheme:"),
                    f"Chunk {chunk['chunk_id']} must have [Scheme: ...] prefix",
                )
                self.assertEqual(chunk["source_url"], doc.source_url)
                self.assertEqual(chunk["last_updated"], doc.last_updated)

    def test_elss_lock_in_content(self):
        elss_doc = self.normalized_docs["hdfc_elss"]
        lock_in_chunk = next(
            c for c in elss_doc.structured_chunks if c["topic"] == "lock_in_period"
        )
        self.assertIn("3 Years", lock_in_chunk["text"])
        self.assertIn("statutory lock-in", lock_in_chunk["text"].lower())


if __name__ == "__main__":
    unittest.main()
