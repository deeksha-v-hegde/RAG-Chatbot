"""
Phase 4: RAG Prompting & Output Synthesis
Module: post_validator.py

Layer 4.2: Output Post-Validation Layer
Validates and guarantees that the generated response strictly adheres to:
1. Sentence count limit (<= 3 sentences)
2. Exact URL rules:
   - For verified facts: exactly 1 whitelisted citation URL
   - For unknown answers or PII: STRICTLY 0 citation URLs
3. Date footer: 'Last updated from sources: <YYYY-MM-DD>' on factual answers
"""

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Any

# Ensure whitelist can be imported
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))

from registry import WHITELISTED_URLS


@dataclass
class ValidationResult:
    is_valid: bool
    cleaned_markdown: str
    sentence_count: int
    url_count: int
    extracted_urls: List[str] = field(default_factory=list)
    has_date_footer: bool = False
    validation_errors: List[str] = field(default_factory=list)


class OutputValidator:
    """Validates and normalizes LLM outputs against regulatory and project constraints."""

    URL_REGEX = re.compile(r"https?://[^\s\)\>\]]+", re.IGNORECASE)
    FOOTER_REGEX = re.compile(r"Last updated from sources:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)

    @classmethod
    def split_sentences(cls, text: str) -> List[str]:
        """Splits text into sentences/statements while preserving bullet points and handling decimals (e.g. 0.74%)."""
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        all_sentences = []
        for line in lines:
            clean_line = re.sub(r"^[-•*]\s*", "", line)
            raw_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", clean_line)
            for s in raw_sentences:
                if s.strip():
                    all_sentences.append(s.strip())
        return all_sentences

    @classmethod
    def validate(
        cls,
        raw_text: str,
        expected_url: Optional[str] = None,
        is_unknown: bool = False,
        is_pii: bool = False,
        last_updated: str = "2026-09-09",
    ) -> ValidationResult:
        """
        Validates and automatically normalizes the response:
        - Limits body to at most 3 sentences or bullet points.
        - Preserves multi-line structured formatting and bullet points.
        - Enforces 0 URLs for unknown/PII responses.
        - Enforces exactly 1 whitelisted URL for known facts.
        - Verifies or attaches the date footer.
        """
        errors = []

        # 1. Parse text into Body, Citation line, and Footer
        lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
        body_lines = []
        source_line = ""
        footer_line = ""

        for line in lines:
            if line.lower().startswith("source:") or (("http://" in line or "https://" in line) and not line.startswith("•")):
                source_line = line
            elif "last updated from sources:" in line.lower():
                footer_line = line
            else:
                body_lines.append(line)

        # Preserve structured line breaks
        body_text = "\n".join(body_lines)
        sentences = cls.split_sentences(body_text)

        # Enforce <= 3 sentences / statements
        if len(sentences) > 3:
            if len(body_lines) > 3:
                body_lines = body_lines[:3]
                body_text = "\n".join(body_lines)
                sentences = cls.split_sentences(body_text)
            if len(sentences) > 3:
                sentences = sentences[:3]
                body_text = " ".join(sentences)

        # 2. Enforce Strict URL Constraints
        extracted_urls = cls.URL_REGEX.findall(raw_text)

        # Case A: Unknown Answer or Personal Information -> STRICTLY 0 URLs
        if is_unknown or is_pii or "unavailable in the current corpus" in body_text.lower() or "not available" in body_text.lower():
            cleaned_markdown = body_text
            return ValidationResult(
                is_valid=True,
                cleaned_markdown=cleaned_markdown,
                sentence_count=len(sentences),
                url_count=0,
                extracted_urls=[],
                has_date_footer=False,
                validation_errors=[],
            )

        # Case B: Known Factual Response -> Exactly 1 Whitelisted URL
        canonical_url = expected_url or (extracted_urls[0] if extracted_urls else "")
        if canonical_url not in WHITELISTED_URLS and canonical_url:
            errors.append(f"Citation URL '{canonical_url}' is not in approved whitelist.")
            if expected_url:
                canonical_url = expected_url

        if not canonical_url and expected_url:
            canonical_url = expected_url

        # Format clean markdown with exactly 1 citation and mandatory footer
        citation_title = "Groww"
        if "mid-cap" in canonical_url:
            citation_title = "Groww - HDFC Mid-Cap Opportunities Fund Direct-Growth"
        elif "equity-fund" in canonical_url:
            citation_title = "Groww - HDFC Flexi Cap Fund Direct-Growth"
        elif "focused" in canonical_url:
            citation_title = "Groww - HDFC Focused 30 Fund Direct-Growth"
        elif "elss" in canonical_url:
            citation_title = "Groww - HDFC ELSS Tax Saver Fund Direct-Growth"
        elif "large-cap" in canonical_url:
            citation_title = "Groww - HDFC Top 100 Fund Direct-Growth"

        cleaned_markdown = (
            f"{body_text}\n\n"
            f"Source: [{citation_title}]({canonical_url})\n"
            f"Last updated from sources: {last_updated}"
        )

        return ValidationResult(
            is_valid=len(errors) == 0,
            cleaned_markdown=cleaned_markdown,
            sentence_count=len(sentences),
            url_count=1 if canonical_url else 0,
            extracted_urls=[canonical_url] if canonical_url else [],
            has_date_footer=True,
            validation_errors=errors,
        )


if __name__ == "__main__":
    # Test 1: Verbose answer (> 3 sentences)
    verbose = (
        "The exit load is 1% if redeemed within 1 year. "
        "No exit load is charged after 1 year. "
        "This is designed to encourage long term investment. "
        "You should plan your investments accordingly. "
        "Additional sentence here."
    )
    res = OutputValidator.validate(
        verbose,
        expected_url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    )
    print("Test 1 (Sentence count trimmed):", res.sentence_count)
    print(res.cleaned_markdown)

    # Test 2: Unknown query (Strict 0 URLs)
    unknown = "This specific detail is not available in the official scheme disclosures."
    res_unk = OutputValidator.validate(unknown, is_unknown=True)
    print("\nTest 2 (Unknown answer URL count):", res_unk.url_count)
    print(res_unk.cleaned_markdown)
