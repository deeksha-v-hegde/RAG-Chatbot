"""
Automated Unit Tests for Phase 1.2: Raw Web Fetching & Snapshot Persistence
Module: test_fetcher.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent / "phase1.1"))

from fetcher import SchemeFetcher
from registry import SchemeRegistry


class TestSchemeFetcher(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.registry = SchemeRegistry()
        cls.fetcher = SchemeFetcher(registry=cls.registry)

    def test_unwhitelisted_url_rejected_by_fetcher(self):
        forbidden_url = "https://groww.in/mutual-funds/sbi-bluechip-fund-direct-growth"
        with self.assertRaises(PermissionError):
            self.fetcher.fetch_url(forbidden_url)

    def test_fetch_and_cache_schemes(self):
        # Fetch all 5 schemes (will create or use cached files)
        results = self.fetcher.fetch_all(delay_seconds=1.0, force_refresh=False)
        self.assertEqual(len(results), 5, "Must fetch all 5 schemes.")

        for scheme in self.registry.get_all():
            html_file = self.fetcher.raw_data_dir / f"{scheme.scheme_id}.html"
            meta_file = self.fetcher.raw_data_dir / f"{scheme.scheme_id}_meta.json"

            self.assertTrue(html_file.exists(), f"Missing HTML snapshot for {scheme.scheme_id}")
            self.assertTrue(meta_file.exists(), f"Missing metadata snapshot for {scheme.scheme_id}")

            # Verify file has substantial content (> 50KB for Groww page)
            file_size = html_file.stat().st_size
            self.assertGreater(file_size, 50000, f"HTML file suspiciously small ({file_size} bytes)")

            # Check that Next.js server data script is present
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("__NEXT_DATA__", content, f"Missing __NEXT_DATA__ in {scheme.scheme_id}")

    def test_cache_reuse(self):
        # When force_refresh=False, it should immediately return the cached file
        target_scheme = "hdfc_mid_cap"
        path = self.fetcher.fetch_and_save_scheme(target_scheme, force_refresh=False)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
