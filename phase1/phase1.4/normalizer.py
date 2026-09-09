"""
Phase 1.4: Normalized Document Generation & Metadata Tagging
Module: normalizer.py

Normalizes extracted scheme data into standardized, ingestion-ready document records
with immutable metadata and atomic semantic chunk blocks ready for Phase 2 indexing.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

import sys
# Add search paths for phase1 modules
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir.parent / "phase1.1"))
sys.path.insert(0, str(current_dir.parent / "phase1.3"))

from registry import SchemeRegistry, WHITELISTED_URLS
from parser import SchemeDOMParser, ParsedSchemeData

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase1.4_Normalizer")


@dataclass
class NormalizedChunk:
    chunk_id: str
    scheme_id: str
    scheme_name: str
    topic: str
    text: str
    source_url: str
    citation_label: str
    last_updated: str


@dataclass
class NormalizedSchemeDocument:
    scheme_id: str
    scheme_name: str
    canonical_name: str
    category: str
    sub_category: str
    plan_type: str
    source_url: str
    citation_label: str
    doc_type: str
    last_updated: str
    sections: Dict[str, Any]
    structured_chunks: List[Dict[str, Any]]
    full_markdown: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SchemeNormalizer:
    """Transforms parsed scheme attributes into standardized documents and semantic chunks."""

    def __init__(
        self,
        extracted_dir: Optional[Path] = None,
        processed_dir: Optional[Path] = None,
        registry: Optional[SchemeRegistry] = None,
    ):
        self.extracted_dir = extracted_dir or self._find_data_dir("extracted")
        self.processed_dir = processed_dir or self._find_data_dir("processed")
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or SchemeRegistry()

    @staticmethod
    def _find_data_dir(subdir: str) -> Path:
        current = Path(__file__).resolve().parent
        for _ in range(4):
            if (current / "corpus").exists() or (current / "docs").exists():
                return current / "data" / subdir
            current = current.parent
        return Path(f"data/{subdir}").resolve()

    def generate_chunks(self, scheme_reg, parsed: Dict[str, Any]) -> List[NormalizedChunk]:
        """Generates atomic, self-contained semantic text chunks with prefix injection."""
        scheme_id = parsed["scheme_id"]
        canonical_name = scheme_reg.canonical_name
        full_name = f"{canonical_name} (Direct Plan - Growth Option)"
        url = scheme_reg.source_url
        citation = scheme_reg.citation_title
        last_updated = parsed.get("last_updated", "2026-09-09")

        chunks = []

        # 1. Expense Ratio (TER)
        ter = parsed["expense_ratio"]
        text_ter = (
            f"[Scheme: {full_name} | Topic: Expense Ratio]\n"
            f"The Expense Ratio (Total Expense Ratio / TER) for {canonical_name} Direct-Growth is {ter}. "
            f"This fee is charged annually by HDFC Mutual Fund for managing the fund."
        )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_ter",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="expense_ratio",
                text=text_ter,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        # 2. Exit Load
        exit_load = parsed["exit_load"]
        text_exit_load = (
            f"[Scheme: {full_name} | Topic: Exit Load]\n"
            f"The exit load for {canonical_name} is: {exit_load}. "
            f"An exit load is the fee deducted if units are redeemed before the specified period."
        )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_exit_load",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="exit_load",
                text=text_exit_load,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        # 3. Minimum Investment & SIP Limits
        min_sip = parsed["min_sip"]
        min_lump = parsed["min_lumpsum"]
        text_invest = (
            f"[Scheme: {full_name} | Topic: Minimum Investment Limits]\n"
            f"For {canonical_name} (Direct Plan - Growth Option), the minimum SIP (Systematic Investment Plan) amount is {min_sip}. "
            f"The minimum initial lumpsum investment amount is {min_lump}."
        )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_investment_limits",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="investment_limits",
                text=text_invest,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        # 4. Riskometer & Benchmark
        riskometer = parsed["riskometer"]
        benchmark = parsed["benchmark"]
        text_risk = (
            f"[Scheme: {full_name} | Topic: Riskometer & Benchmark]\n"
            f"The official SEBI Riskometer rating for {canonical_name} is '{riskometer}'. "
            f"The underlying benchmark index against which performance is measured is '{benchmark}'."
        )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_risk_benchmark",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="riskometer_and_benchmark",
                text=text_risk,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        # 5. Lock-in Period
        lock_in = parsed["lock_in"]
        lock_years = parsed.get("lock_in_years")
        if lock_years == 3 or "elss" in scheme_id:
            text_lock = (
                f"[Scheme: {full_name} | Topic: Statutory Lock-in Period]\n"
                f"{canonical_name} is an ELSS (Equity Linked Savings Scheme) with a mandatory statutory lock-in period of 3 Years. "
                f"Units cannot be redeemed, transferred, or switched before the completion of 3 years from the date of allotment."
            )
        else:
            text_lock = (
                f"[Scheme: {full_name} | Topic: Lock-in Period]\n"
                f"{canonical_name} has no lock-in period ({lock_in}). "
                f"Investors can redeem their units at any time, subject to applicable exit load and taxes."
            )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_lock_in",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="lock_in_period",
                text=text_lock,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        # 6. Fund Management & Launch
        mgr = parsed["fund_managers"]
        launch = parsed["launch_date"]
        desc = parsed["fund_description"]
        tax = parsed["tax_implications"]
        stamp = parsed["stamp_duty"]
        text_mgmt = (
            f"[Scheme: {full_name} | Topic: Fund Management & Overview]\n"
            f"{canonical_name} was launched on {launch} and is managed by {mgr}. "
            f"Objective: {desc} Tax rules: {tax} Stamp duty: {stamp}."
        )
        chunks.append(
            NormalizedChunk(
                chunk_id=f"{scheme_id}_overview",
                scheme_id=scheme_id,
                scheme_name=full_name,
                topic="overview_and_tax",
                text=text_mgmt,
                source_url=url,
                citation_label=citation,
                last_updated=last_updated,
            )
        )

        return chunks

    def generate_markdown(self, doc_data: Dict[str, Any], chunks: List[NormalizedChunk]) -> str:
        """Generates clean human-readable Markdown documentation for the scheme."""
        lines = [
            f"# Scheme Document: {doc_data['canonical_name']}",
            "",
            f"- **Scheme ID:** `{doc_data['scheme_id']}`",
            f"- **Category:** {doc_data['category']} ({doc_data['sub_category']})",
            f"- **Plan Type:** {doc_data['plan_type']}",
            f"- **Official Source URL:** [{doc_data['citation_label']}]({doc_data['source_url']})",
            f"- **Document Type:** {doc_data['doc_type']}",
            f"- **Last Updated:** {doc_data['last_updated']}",
            "",
            "## 1. Key Factual Metrics",
            "",
            "| Metric | Value | Description |",
            "| :--- | :--- | :--- |",
            f"| **Expense Ratio (TER)** | {doc_data['sections']['expense_ratio']} | Annual management fee percentage |",
            f"| **Exit Load** | {doc_data['sections']['exit_load']} | Penalty on early redemption |",
            f"| **Minimum SIP** | {doc_data['sections']['min_sip']} | Minimum monthly SIP amount |",
            f"| **Minimum Lumpsum** | {doc_data['sections']['min_lumpsum']} | Minimum initial investment |",
            f"| **Riskometer** | {doc_data['sections']['riskometer']} | Official SEBI risk classification |",
            f"| **Benchmark** | {doc_data['sections']['benchmark']} | Reference index benchmark |",
            f"| **Lock-in Period** | {doc_data['sections']['lock_in']} | Statutory lock-in duration |",
            f"| **Fund Manager** | {doc_data['sections']['fund_managers']} | Portfolio manager |",
            f"| **Launch Date** | {doc_data['sections']['launch_date']} | Inception / launch date |",
            f"| **Stamp Duty** | {doc_data['sections']['stamp_duty']} | Regulatory stamp duty |",
            "",
            "## 2. Tax Implications & Notes",
            f"> {doc_data['sections']['tax_implications']}",
            "",
            "## 3. Atomic Semantic Chunks for Indexing",
            "",
        ]

        for chunk in chunks:
            lines.append(f"### Chunk `{chunk.chunk_id}` (`{chunk.topic}`)")
            lines.append("```text")
            lines.append(chunk.text)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def normalize_scheme(self, scheme_id: str) -> NormalizedSchemeDocument:
        """Normalizes a single scheme from extracted data and registry."""
        scheme_reg = self.registry.get_by_id(scheme_id)
        if not scheme_reg:
            raise ValueError(f"Scheme ID '{scheme_id}' not found in registry.")

        extracted_file = self.extracted_dir / f"{scheme_id}.json"
        if not extracted_file.exists():
            # If extracted file missing, run parser on the fly
            parser = SchemeDOMParser()
            parsed_obj = parser.parse_scheme_file(scheme_id)
            parsed_data = parsed_obj.to_dict()
        else:
            with open(extracted_file, "r", encoding="utf-8") as f:
                parsed_data = json.load(f)

        chunks = self.generate_chunks(scheme_reg, parsed_data)
        chunks_dict_list = [asdict(c) for c in chunks]

        doc_dict = {
            "scheme_id": scheme_id,
            "scheme_name": parsed_data["scheme_name"],
            "canonical_name": scheme_reg.canonical_name,
            "category": parsed_data["category"],
            "sub_category": parsed_data["sub_category"],
            "plan_type": "Direct Plan - Growth Option",
            "source_url": scheme_reg.source_url,
            "citation_label": scheme_reg.citation_title,
            "doc_type": "Scheme Overview",
            "last_updated": parsed_data.get("last_updated", "2026-09-09"),
            "sections": {
                "expense_ratio": parsed_data["expense_ratio"],
                "expense_ratio_val": parsed_data["expense_ratio_val"],
                "exit_load": parsed_data["exit_load"],
                "min_sip": parsed_data["min_sip"],
                "min_sip_val": parsed_data["min_sip_val"],
                "min_lumpsum": parsed_data["min_lumpsum"],
                "min_lumpsum_val": parsed_data["min_lumpsum_val"],
                "riskometer": parsed_data["riskometer"],
                "benchmark": parsed_data["benchmark"],
                "lock_in": parsed_data["lock_in"],
                "lock_in_years": parsed_data.get("lock_in_years"),
                "fund_managers": parsed_data["fund_managers"],
                "launch_date": parsed_data["launch_date"],
                "tax_implications": parsed_data["tax_implications"],
                "fund_description": parsed_data["fund_description"],
                "stamp_duty": parsed_data["stamp_duty"],
            },
            "structured_chunks": chunks_dict_list,
        }

        markdown_content = self.generate_markdown(doc_dict, chunks)
        doc_dict["full_markdown"] = markdown_content

        norm_doc = NormalizedSchemeDocument(**doc_dict)

        # Write processed JSON
        json_out = self.processed_dir / f"{scheme_id}.json"
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(norm_doc.to_dict(), f, indent=2, ensure_ascii=False)

        # Write processed Markdown
        md_out = self.processed_dir / f"{scheme_id}.md"
        with open(md_out, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        logger.info(f"Successfully normalized: {scheme_id} -> {json_out.name} & {md_out.name}")
        return norm_doc

    def normalize_all(self) -> Dict[str, NormalizedSchemeDocument]:
        """Normalizes all 5 registered schemes."""
        results = {}
        for scheme in self.registry.get_all():
            results[scheme.scheme_id] = self.normalize_scheme(scheme.scheme_id)
        return results


if __name__ == "__main__":
    normalizer = SchemeNormalizer()
    docs = normalizer.normalize_all()
    print("\n✓ Normalization complete for all schemes:")
    for sid, doc in docs.items():
        print(f"  [{sid}] Chunks: {len(doc.structured_chunks)} | URL: {doc.source_url}")
