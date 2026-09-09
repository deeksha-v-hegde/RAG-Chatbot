"""
Phase 1.5: Ingestion Validation & Integrity Verification
Module: validator.py

Executes rigorous compliance and data integrity assertions across all processed
mutual fund documents in data/processed/, generating an authoritative Ingestion Audit Report.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

import sys
# Add search paths for phase1 modules
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir.parent / "phase1.1"))

from registry import WHITELISTED_URLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase1.5_Validator")

REQUIRED_SECTIONS = [
    "expense_ratio",
    "exit_load",
    "min_sip",
    "min_lumpsum",
    "riskometer",
    "benchmark",
    "lock_in",
    "fund_managers",
    "launch_date",
]

EXPECTED_SCHEME_IDS = [
    "hdfc_mid_cap",
    "hdfc_flexi_cap",
    "hdfc_focused",
    "hdfc_elss",
    "hdfc_large_cap",
]


class IngestionValidator:
    """Validates processed mutual fund documents and produces an audit report."""

    def __init__(
        self,
        processed_dir: Optional[Path] = None,
        report_file: Optional[Path] = None,
    ):
        self.processed_dir = processed_dir or self._find_data_dir("processed")
        self.report_file = report_file or self._find_data_dir("ingestion_report.json")

    @staticmethod
    def _find_data_dir(target_name: str) -> Path:
        current = Path(__file__).resolve().parent
        for _ in range(4):
            if (current / "corpus").exists() or (current / "docs").exists():
                return current / "data" / target_name
            current = current.parent
        return Path(f"data/{target_name}").resolve()

    def validate_single_scheme(self, scheme_id: str) -> Dict[str, Any]:
        """Validates a single processed scheme document."""
        json_file = self.processed_dir / f"{scheme_id}.json"
        md_file = self.processed_dir / f"{scheme_id}.md"

        errors: List[str] = []
        checks_passed: List[str] = []

        if not json_file.exists():
            return {
                "scheme_id": scheme_id,
                "status": "FAIL",
                "errors": [f"Missing processed JSON file: {json_file.name}"],
            }

        if not md_file.exists():
            errors.append(f"Missing processed Markdown file: {md_file.name}")
        else:
            checks_passed.append("Markdown file present")

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. URL Whitelist Check
        url = data.get("source_url")
        if url not in WHITELISTED_URLS:
            errors.append(f"Source URL '{url}' violates strict whitelist")
        else:
            checks_passed.append("Source URL in whitelist")

        # 2. Scheme Identification
        if not data.get("scheme_name") or not data.get("canonical_name"):
            errors.append("Missing scheme_name or canonical_name")
        else:
            checks_passed.append("Valid scheme identification")

        # 3. Required Sections
        sections = data.get("sections", {})
        for req_field in REQUIRED_SECTIONS:
            val = sections.get(req_field)
            if val is None or val == "" or val == "—":
                errors.append(f"Required field '{req_field}' is missing or empty")
            else:
                checks_passed.append(f"Field '{req_field}' populated: {val}")

        # 4. Expense Ratio format check
        ter = sections.get("expense_ratio", "")
        if not ter.endswith("%") or sections.get("expense_ratio_val", 0.0) <= 0.0:
            errors.append(f"Invalid expense ratio format/value: {ter}")
        else:
            checks_passed.append("Valid expense ratio format")

        # 5. Min SIP check
        min_sip_val = sections.get("min_sip_val", 0)
        if min_sip_val < 100:
            errors.append(f"Min SIP must be at least ₹100, found: {min_sip_val}")
        else:
            checks_passed.append("Min SIP valid")

        # 6. Statutory Lock-in for ELSS check
        if scheme_id == "hdfc_elss":
            lock_years = sections.get("lock_in_years")
            lock_str = sections.get("lock_in", "")
            if lock_years != 3 or "3 Years" not in lock_str:
                errors.append(f"ELSS must have exactly 3 years statutory lock-in, got: {lock_str}")
            else:
                checks_passed.append("Statutory 3-year lock-in verified for ELSS")

        # 7. Chunks check
        chunks = data.get("structured_chunks", [])
        if len(chunks) < 6:
            errors.append(f"Expected at least 6 structured chunks, found: {len(chunks)}")
        else:
            checks_passed.append(f"{len(chunks)} structured chunks validated")

        status = "FAIL" if errors else "PASS"
        return {
            "scheme_id": scheme_id,
            "scheme_name": data.get("canonical_name", scheme_id),
            "status": status,
            "errors": errors,
            "checks_passed_count": len(checks_passed),
            "sample_metrics": {
                "ter": sections.get("expense_ratio"),
                "exit_load": sections.get("exit_load"),
                "min_sip": sections.get("min_sip"),
                "riskometer": sections.get("riskometer"),
                "benchmark": sections.get("benchmark"),
                "lock_in": sections.get("lock_in"),
            },
        }

    def validate_corpus(self) -> Dict[str, Any]:
        """Runs validation across all 5 schemes and writes data/ingestion_report.json."""
        timestamp = datetime.now(timezone.utc).isoformat()
        scheme_reports = []
        overall_errors = []

        # Check total scheme count in processed dir
        existing_jsons = list(self.processed_dir.glob("*.json"))
        if len(existing_jsons) != len(EXPECTED_SCHEME_IDS):
            overall_errors.append(
                f"Expected exactly {len(EXPECTED_SCHEME_IDS)} JSON files in processed dir, found {len(existing_jsons)}."
            )

        for sid in EXPECTED_SCHEME_IDS:
            rep = self.validate_single_scheme(sid)
            scheme_reports.append(rep)
            if rep["status"] == "FAIL":
                overall_errors.extend([f"[{sid}] {e}" for e in rep["errors"]])

        is_passed = len(overall_errors) == 0
        overall_status = "PASSED" if is_passed else "FAILED"

        report = {
            "report_name": "Phase 1 Ingestion Integrity & Compliance Audit",
            "generated_at_utc": timestamp,
            "status": overall_status,
            "total_schemes_expected": len(EXPECTED_SCHEME_IDS),
            "total_schemes_verified": len(scheme_reports),
            "all_checks_passed": is_passed,
            "summary_errors": overall_errors,
            "schemes": scheme_reports,
        }

        # Write report file
        self.report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        if is_passed:
            logger.info(f"✓ Ingestion Audit PASSED (100% integrity across all 5 schemes) -> {self.report_file.name}")
        else:
            logger.error(f"✗ Ingestion Audit FAILED with {len(overall_errors)} errors -> {self.report_file.name}")

        return report


if __name__ == "__main__":
    validator = IngestionValidator()
    result = validator.validate_corpus()
    print(f"\nFinal Ingestion Audit Status: {result['status']}")
    for s in result["schemes"]:
        print(f"  [{s['status']}] {s['scheme_id']}: {s['scheme_name']} ({s['checks_passed_count']} checks passed)")
