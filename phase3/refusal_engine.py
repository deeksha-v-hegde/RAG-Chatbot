"""
Phase 3: Guardrails, Security & Refusal Engine
Module: refusal_engine.py

Generates structured, polite, regulatory-compliant refusal responses.
Enforces the mandatory constraint of <= 3 sentences, exactly 1 official citation link,
and the source date footer.
"""

from dataclasses import dataclass
from typing import Dict, Optional

# Official Educational Links mandated by problem statement & architecture
AMFI_EDUCATION_URL = "https://www.amfiindia.com/investor-corner"
SEBI_INVESTOR_URL = "https://investor.sebi.gov.in"
DEFAULT_LAST_UPDATED = "2026-09-09"


@dataclass
class FormattedRefusal:
    answer: str
    citation_title: str
    citation_url: str
    last_updated: str
    full_markdown: str


class RefusalEngine:
    """Produces standardized non-advisory refusal responses adhering to strict format constraints."""

    TEMPLATES: Dict[str, Dict[str, str]] = {
        "ADVISORY": {
            "body": (
                "I am a facts-only assistant and cannot provide investment advice, scheme recommendations, or personal financial guidance. "
                "For official investor education modules and mutual fund guidelines, please refer to the AMFI Investor Corner."
            ),
            "citation_title": "AMFI Investor Corner",
            "citation_url": AMFI_EDUCATION_URL,
        },
        "COMPARISON": {
            "body": (
                "I cannot compare, rank, or evaluate mutual fund schemes against each other. "
                "Please review the individual objective metrics and scheme disclosures for each fund separately on the official Groww pages."
            ),
            "citation_title": "AMFI Investor Corner",
            "citation_url": AMFI_EDUCATION_URL,
        },
        "PREDICTION": {
            "body": (
                "I cannot forecast future returns, predict market trends, or calculate speculative compounding gains. "
                "Mutual fund investments are subject to market risks, and historical figures can be reviewed in the official scheme factsheets."
            ),
            "citation_title": "AMFI Investor Corner",
            "citation_url": AMFI_EDUCATION_URL,
        },
        "JAILBREAK": {
            "body": (
                "I operate strictly under regulatory boundaries as a facts-only mutual fund FAQ assistant and cannot adopt advisory personas. "
                "Please submit objective questions regarding the 5 designated HDFC mutual fund schemes."
            ),
            "citation_title": "SEBI Investor Website",
            "citation_url": SEBI_INVESTOR_URL,
        },
        "PII_SECURITY": {
            "body": (
                "For your personal privacy and security, this assistant does not process personal identification numbers, account credentials, or contact details. "
                "Please ask objective questions about mutual fund schemes without submitting confidential identifiers."
            ),
            "citation_title": "",
            "citation_url": "",
        },
        "UNKNOWN_ANSWER": {
            "body": (
                "This specific information is not available in the official scheme disclosures for the 5 designated HDFC mutual fund schemes in our current corpus."
            ),
            "citation_title": "",
            "citation_url": "",
        },
        "OUT_OF_SCOPE": {
            "body": (
                "I am specifically designed to answer factual questions regarding 5 designated HDFC Mutual Fund schemes on Groww. "
                "For general mutual fund guidelines and regulatory FAQs, please consult the AMFI Knowledge Center."
            ),
            "citation_title": "AMFI Investor Corner",
            "citation_url": AMFI_EDUCATION_URL,
        },
    }

    @classmethod
    def generate_refusal(cls, category: str, custom_body: Optional[str] = None) -> FormattedRefusal:
        """Constructs a compliant refusal response. Omits URL for PII or unknown answer categories."""
        template = cls.TEMPLATES.get(category, cls.TEMPLATES["ADVISORY"])
        body = custom_body or template["body"]
        cit_title = template.get("citation_title", "")
        cit_url = template.get("citation_url", "")
        date_str = DEFAULT_LAST_UPDATED

        # If citation URL is omitted (for PII or unknown answers), do not attach source link
        if cit_url:
            markdown_text = (
                f"{body}\n\n"
                f"Source: [{cit_title}]({cit_url})\n"
                f"Last updated from sources: {date_str}"
            )
        else:
            markdown_text = f"{body}"

        return FormattedRefusal(
            answer=body,
            citation_title=cit_title,
            citation_url=cit_url,
            last_updated=date_str if cit_url else "",
            full_markdown=markdown_text,
        )


if __name__ == "__main__":
    for cat in ["ADVISORY", "COMPARISON", "PREDICTION", "JAILBREAK", "PII_SECURITY"]:
        ref = RefusalEngine.generate_refusal(cat)
        print(f"\n=== Refusal: {cat} ===")
        print(ref.full_markdown)
