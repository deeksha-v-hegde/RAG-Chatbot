"""
Phase 1.6: Ingestion Pipeline Orchestrator & CLI Runner
Module: pipeline.py

Chains together Subphases 1.1 through 1.5 into an end-to-end executable pipeline
with CLI commands, robust logging, progress indicators, and comprehensive error handling.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any

# Setup search paths for phase1 submodules
current_dir = Path(__file__).resolve().parent
phase1_root = current_dir.parent
sys.path.insert(0, str(phase1_root / "phase1.1"))
sys.path.insert(0, str(phase1_root / "phase1.2"))
sys.path.insert(0, str(phase1_root / "phase1.3"))
sys.path.insert(0, str(phase1_root / "phase1.4"))
sys.path.insert(0, str(phase1_root / "phase1.5"))

from registry import SchemeRegistry
from fetcher import SchemeFetcher
from parser import SchemeDOMParser
from normalizer import SchemeNormalizer
from validator import IngestionValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase1_Orchestrator")


class IngestionPipeline:
    """Orchestrates the complete Phase 1 ingestion lifecycle."""

    def __init__(self, force_refresh: bool = False):
        self.force_refresh = force_refresh
        self.registry = None
        self.fetcher = None
        self.parser = None
        self.normalizer = None
        self.validator = None

    def run(self) -> Dict[str, Any]:
        """Executes Subphases 1.1 to 1.5 sequentially."""
        logger.info("==========================================================")
        logger.info("  STARTING PHASE 1: CORPUS INGESTION & AUDIT PIPELINE")
        logger.info("==========================================================")

        # ------------------------------------------------------------------
        # Step 1: Subphase 1.1 - Registry & Whitelist Verification
        # ------------------------------------------------------------------
        logger.info("\n>>> [1/5] Executing Subphase 1.1: Registry & Whitelist Verification")
        self.registry = SchemeRegistry()
        schemes = self.registry.get_all()
        logger.info(f"Loaded {len(schemes)} whitelisted scheme definitions from sources.json.")
        for s in schemes:
            logger.info(f"  • {s.scheme_id}: {s.canonical_name} ({s.category})")

        # ------------------------------------------------------------------
        # Step 2: Subphase 1.2 - Raw Web Fetching & Snapshot Persistence
        # ------------------------------------------------------------------
        logger.info("\n>>> [2/5] Executing Subphase 1.2: Raw Web Fetching & Caching")
        self.fetcher = SchemeFetcher(registry=self.registry)
        cached_snapshots = self.fetcher.fetch_all(
            delay_seconds=1.0,
            force_refresh=self.force_refresh,
        )
        logger.info(f"Retrieved {len(cached_snapshots)} raw page snapshots in data/raw/.")

        # ------------------------------------------------------------------
        # Step 3: Subphase 1.3 - DOM Parsing & Section Extraction
        # ------------------------------------------------------------------
        logger.info("\n>>> [3/5] Executing Subphase 1.3: DOM Parsing & Metric Extraction")
        self.parser = SchemeDOMParser()
        parsed_data = self.parser.parse_all()
        logger.info(f"Extracted key factual metrics for {len(parsed_data)} schemes in data/extracted/.")

        # ------------------------------------------------------------------
        # Step 4: Subphase 1.4 - Normalized Documents & Chunk Generation
        # ------------------------------------------------------------------
        logger.info("\n>>> [4/5] Executing Subphase 1.4: Document Normalization & Semantic Chunking")
        self.normalizer = SchemeNormalizer(registry=self.registry)
        normalized_docs = self.normalizer.normalize_all()
        total_chunks = sum(len(d.structured_chunks) for d in normalized_docs.values())
        logger.info(f"Generated {len(normalized_docs)} standardized documents ({total_chunks} total chunks) in data/processed/.")

        # ------------------------------------------------------------------
        # Step 5: Subphase 1.5 - Ingestion Validation & Audit Report
        # ------------------------------------------------------------------
        logger.info("\n>>> [5/5] Executing Subphase 1.5: Ingestion Validation & Compliance Audit")
        self.validator = IngestionValidator()
        audit_report = self.validator.validate_corpus()

        logger.info("==========================================================")
        logger.info(f"  PHASE 1 INGESTION COMPLETE - STATUS: {audit_report['status']}")
        logger.info(f"  Total Schemes Verified: {audit_report['total_schemes_verified']}/{audit_report['total_schemes_expected']}")
        logger.info(f"  Audit Report Path: {self.validator.report_file}")
        logger.info("==========================================================")

        return {
            "status": audit_report["status"],
            "schemes_count": len(normalized_docs),
            "chunks_count": total_chunks,
            "report_path": str(self.validator.report_file),
            "audit_report": audit_report,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: Mutual Fund Knowledge Corpus Ingestion Pipeline"
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Bypass cached raw HTML snapshots and re-fetch from live Groww pages.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Run Subphase 1.5 validation checks on existing data/processed/ without re-ingesting.",
    )

    args = parser.parse_args()

    if args.validate_only:
        logger.info("Running Phase 1.5 Validation Checks Only...")
        validator = IngestionValidator()
        report = validator.validate_corpus()
        sys.exit(0 if report["all_checks_passed"] else 1)

    pipeline = IngestionPipeline(force_refresh=args.force_refresh)
    result = pipeline.run()

    if result["status"] != "PASSED":
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
