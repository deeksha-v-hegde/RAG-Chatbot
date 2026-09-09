"""
Phase 4: RAG Prompting & Output Synthesis
Test Suite: test_phase4.py

Validates compliance with Phase 4 architecture and all regulatory/system constraints:
1. Sentence count limit (<= 3 sentences)
2. Strict URL rules:
   - Exactly 1 whitelisted URL on factual responses
   - STRICTLY 0 URLs on unknown answers
   - STRICTLY 0 URLs on PII queries
   - STRICTLY 0 URLs on foreign AMC out-of-scope queries
   - STRICTLY 0 URLs on disambiguation requests
3. Presence of 'Last updated from sources:' footer on factual responses
4. Advisory rejection with educational link
"""

import unittest
import sys
from pathlib import Path

# Add paths
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))
sys.path.insert(0, str(project_root / "phase2"))
sys.path.insert(0, str(project_root / "phase3"))
sys.path.insert(0, str(current_dir))

from registry import WHITELISTED_URLS
from post_validator import OutputValidator, ValidationResult
from prompt_templates import PromptBuilder, SYSTEM_PROMPT
from synthesizer import RAGSynthesizer, SynthesizerResponse


class TestPhase4RAGSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.synthesizer = RAGSynthesizer()

    def test_01_factual_query_hdfc_midcap_exit_load(self):
        """Test factual retrieval: exit load for HDFC Mid Cap."""
        resp = self.synthesizer.answer_query("What is the exit load for HDFC Mid Cap?")
        self.assertFalse(resp.is_refusal)
        self.assertFalse(resp.is_unknown)
        self.assertLessEqual(resp.sentence_count, 3, "Must be <= 3 sentences")
        self.assertEqual(resp.url_count, 1, "Must contain exactly 1 citation URL")
        self.assertIn("https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth", resp.source_url)
        self.assertIn("Last updated from sources:", resp.markdown_output)
        self.assertIn("1%", resp.answer)

    def test_02_factual_query_hdfc_flexicap_expense_ratio(self):
        """Test factual retrieval: expense ratio for HDFC Flexi Cap."""
        resp = self.synthesizer.answer_query("Tell me the expense ratio of HDFC Flexicap")
        self.assertFalse(resp.is_refusal)
        self.assertFalse(resp.is_unknown)
        self.assertLessEqual(resp.sentence_count, 3, "Must be <= 3 sentences")
        self.assertEqual(resp.url_count, 1, "Must contain exactly 1 citation URL")
        self.assertIn("https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth", resp.source_url)
        self.assertIn("0.77%", resp.answer)
        self.assertIn("Last updated from sources:", resp.markdown_output)

    def test_03_factual_query_hdfc_elss_lock_in(self):
        """Test factual retrieval: 3-year statutory lock-in for HDFC ELSS."""
        resp = self.synthesizer.answer_query("What is the lock-in period for HDFC ELSS Tax Saver?")
        self.assertFalse(resp.is_refusal)
        self.assertLessEqual(resp.sentence_count, 3)
        self.assertEqual(resp.url_count, 1)
        self.assertIn("https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth", resp.source_url)
        self.assertIn("3 Year", resp.answer)
        self.assertIn("Last updated from sources:", resp.markdown_output)

    def test_04_advisory_rejection_with_amfi_link(self):
        """Test that investment advice queries are refused with an educational link."""
        resp = self.synthesizer.answer_query("Which fund should I buy for high returns in 5 years?")
        self.assertTrue(resp.is_refusal)
        self.assertLessEqual(resp.sentence_count, 3)
        self.assertEqual(resp.url_count, 1)
        self.assertIn("amfiindia.com", resp.source_url)
        self.assertIn("cannot provide investment advice", resp.answer.lower())

    def test_05_pii_interception_strict_zero_urls(self):
        """CRITICAL CONSTRAINT: Queries with personal information must have ZERO URLs attached."""
        resp = self.synthesizer.answer_query("My PAN card is ABCDE1234F, tell me my HDFC folio balance.")
        self.assertTrue(resp.is_refusal)
        self.assertEqual(resp.url_count, 0, "PII responses must NEVER attach any citation URL")
        self.assertEqual(resp.source_url, "")
        self.assertNotIn("http://", resp.markdown_output)
        self.assertNotIn("https://", resp.markdown_output)
        self.assertIn("Security Notice", resp.answer)

    def test_06_disambiguation_missing_scheme_zero_urls(self):
        """Test that metric queries without scheme specify disambiguation with 0 URLs."""
        resp = self.synthesizer.answer_query("What is the exit load?")
        self.assertTrue(resp.is_disambiguation)
        self.assertEqual(resp.url_count, 0, "Disambiguation prompt must not attach a URL")
        self.assertIn("Please specify which HDFC fund", resp.answer)

    def test_07_out_of_scope_foreign_amc_zero_urls(self):
        """Test boundary gate: Non-HDFC AMC queries are rejected with 0 URLs."""
        resp = self.synthesizer.answer_query("What is the NAV of SBI Bluechip Fund?")
        self.assertTrue(resp.is_refusal)
        self.assertEqual(resp.url_count, 0, "Foreign AMC query must have 0 URLs attached")
        self.assertIn("Out of Scope", resp.answer)
        self.assertNotIn("https://", resp.markdown_output)

    def test_08_unknown_answer_strict_zero_urls(self):
        """CRITICAL CONSTRAINT: Unknown answers must have ZERO URLs attached."""
        # Simulated unknown validation
        unknown_text = "This specific information is not available in the official scheme disclosures."
        val = OutputValidator.validate(unknown_text, is_unknown=True)
        self.assertEqual(val.url_count, 0, "Unknown answers must have 0 URLs")
        self.assertEqual(val.extracted_urls, [])
        self.assertNotIn("Source:", val.cleaned_markdown)

    def test_09_sentence_limiter_truncates_to_three(self):
        """Test post-validator enforces at most 3 sentences."""
        long_text = "Sentence 1. Sentence 2. Sentence 3. Sentence 4. Sentence 5."
        val = OutputValidator.validate(
            long_text,
            expected_url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        )
        self.assertLessEqual(val.sentence_count, 3)
        self.assertNotIn("Sentence 4", val.cleaned_markdown)


if __name__ == "__main__":
    unittest.main()
