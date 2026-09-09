"""
Phase 5: Minimal Web Interface & API Layer
Test Suite: test_phase5.py

Tests FastAPI endpoints, static asset serving, and regulatory compliance via TestClient.
"""

import unittest
import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

from fastapi.testclient import TestClient
from api import app


class TestPhase5API(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_endpoint(self):
        """GET /health must return 200 and report 5 designated schemes."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["designated_schemes_count"], 5)
        self.assertEqual(data["corpus_amc"], "HDFC Mutual Fund")

    def test_02_schemes_endpoint(self):
        """GET /api/schemes must return the 5 canonical schemes with official Groww URLs."""
        response = self.client.get("/api/schemes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 5)
        scheme_ids = [s["scheme_id"] for s in data]
        self.assertIn("hdfc_mid_cap", scheme_ids)
        self.assertIn("hdfc_flexi_cap", scheme_ids)
        self.assertIn("hdfc_focused", scheme_ids)
        self.assertIn("hdfc_elss", scheme_ids)
        self.assertIn("hdfc_large_cap", scheme_ids)

    def test_03_chat_factual_query(self):
        """POST /api/chat must return accurate answer, <=3 sentences, and 1 citation URL."""
        response = self.client.post(
            "/api/chat",
            json={"query": "What is the exit load for HDFC Mid-Cap Opportunities Fund?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data["is_refusal"])
        self.assertLessEqual(data["sentence_count"], 3)
        self.assertEqual(data["url_count"], 1)
        self.assertIn("https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth", data["citation_url"])
        self.assertIn("1%", data["answer"])

    def test_04_chat_advisory_refusal(self):
        """POST /api/chat must politely refuse investment advice with an AMFI link."""
        response = self.client.post(
            "/api/chat",
            json={"query": "Should I invest in HDFC Top 100 for 5 years?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_refusal"])
        self.assertEqual(data["url_count"], 1)
        self.assertIn("amfiindia.com", data["citation_url"])

    def test_05_chat_pii_defense_strict_zero_urls(self):
        """CRITICAL: Queries containing PII must trigger privacy notice with STRICTLY ZERO URLs."""
        response = self.client.post(
            "/api/chat",
            json={"query": "My PAN is ABCDE1234F, check my folio balance."},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_refusal"])
        self.assertEqual(data["url_count"], 0, "PII responses must NEVER attach any citation URL")
        self.assertEqual(data["citation_url"], "")
        self.assertIn("Security Notice", data["answer"])

    def test_06_chat_disambiguation_zero_urls(self):
        """Ambiguous query without a scheme must trigger disambiguation with ZERO URLs."""
        response = self.client.post(
            "/api/chat",
            json={"query": "What is the exit load?"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["is_disambiguation"])
        self.assertEqual(data["url_count"], 0)
        self.assertIn("Please specify which HDFC fund", data["answer"])

    def test_07_serve_index_html(self):
        """GET / must serve frontend index.html with the regulatory banner."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Facts-only. No investment advice.", response.text)
        self.assertIn("Groww MF Assistant", response.text)


if __name__ == "__main__":
    unittest.main()
