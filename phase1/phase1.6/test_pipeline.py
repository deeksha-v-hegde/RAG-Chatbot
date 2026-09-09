"""
Automated Unit Tests for Phase 1.6: Ingestion Pipeline Orchestrator
Module: test_pipeline.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from pipeline import IngestionPipeline


class TestIngestionPipeline(unittest.TestCase):

    def test_pipeline_execution_and_artifacts(self):
        pipeline = IngestionPipeline(force_refresh=False)
        result = pipeline.run()

        self.assertEqual(result["status"], "PASSED")
        self.assertEqual(result["schemes_count"], 5)
        self.assertEqual(result["chunks_count"], 30)  # 6 chunks * 5 schemes = 30 chunks
        self.assertTrue(result["audit_report"]["all_checks_passed"])

        # Assert report file exists
        report_path = Path(result["report_path"])
        self.assertTrue(report_path.exists())


if __name__ == "__main__":
    unittest.main()
