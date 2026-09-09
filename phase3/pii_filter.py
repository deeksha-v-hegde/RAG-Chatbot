"""
Phase 3: Guardrails, Security & Refusal Engine
Module: pii_filter.py

Layer 1: Detects and blocks sensitive Personally Identifiable Information (PII)
including PAN cards, Aadhaar numbers, phone numbers, emails, OTPs, and bank accounts.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PIICheckResult:
    has_pii: bool
    detected_types: List[str] = field(default_factory=list)
    sanitized_query: str = ""
    security_message: Optional[str] = None


class PIIFilter:
    """Scans and intercepts user inputs containing sensitive personal/financial data."""

    # Regex patterns for Indian financial & personal identifiers
    PATTERNS = {
        "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b", re.IGNORECASE),
        "Aadhaar": re.compile(r"\b[0-9]{4}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b|\b(?:aadhaar|aadhar)\s+(?:no\.?|number|#)?\s*[:=]?\s*[0-9\s-]{12,16}\b", re.IGNORECASE),
        "Phone": re.compile(r"\b(?:\+91[\-\s]?)?[6-9]\d{9}\b"),
        "Email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "OTP_PIN": re.compile(r"\b(?:otp|pin|cvv|one[- ]time[- ]password)\b[^\d]{0,15}\b[0-9]{4,8}\b", re.IGNORECASE),
        "BankAccount_Folio": re.compile(r"\b(?:account|acc|folio|a/c)\s*(?:no\.?|number|#)?\s*(?:is\s*)?[:=]?\s*(\d{6,18})\b", re.IGNORECASE),
    }

    @classmethod
    def check(cls, text: str) -> PIICheckResult:
        """Evaluates input text for sensitive PII. Returns check result."""
        detected = []

        for pii_type, pattern in cls.PATTERNS.items():
            if pattern.search(text):
                detected.append(pii_type)

        if detected:
            msg = (
                f"Security Notice: For your privacy and security, this assistant does not process personal or confidential details ({', '.join(detected)}). "
                "Please submit only objective questions about mutual fund schemes without including personal account identifiers."
            )
            return PIICheckResult(
                has_pii=True,
                detected_types=detected,
                sanitized_query=text,
                security_message=msg,
            )

        return PIICheckResult(
            has_pii=False,
            detected_types=[],
            sanitized_query=text,
            security_message=None,
        )


if __name__ == "__main__":
    test_samples = [
        "My PAN is ABCDE1234F, can you check my fund?",
        "My OTP is 482910, please update account",
        "Reach me at 9876543210 or user@test.com",
        "What is the exit load for HDFC Mid Cap?",
    ]
    for sample in test_samples:
        res = PIIFilter.check(sample)
        print(f"Text: '{sample}' -> Has PII: {res.has_pii} (Detected: {res.detected_types})")
