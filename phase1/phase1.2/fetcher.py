"""
Phase 1.2: Raw Web Fetching & Snapshot Persistence
Module: fetcher.py

Fetches and caches raw HTML page snapshots for the 5 whitelisted Groww HDFC mutual fund URLs.
Enforces strict URL whitelist checks, browser header emulation, and local persistence.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import requests

# Ensure phase1.1 modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "phase1.1"))
from registry import SchemeRegistry, WHITELISTED_URLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase1.2_Fetcher")

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


class SchemeFetcher:
    """Fetches and caches raw HTML snapshots for whitelisted mutual fund URLs."""

    def __init__(self, raw_data_dir: Optional[Path] = None, registry: Optional[SchemeRegistry] = None):
        self.raw_data_dir = raw_data_dir or self._find_raw_data_dir()
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or SchemeRegistry()
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    @staticmethod
    def _find_raw_data_dir() -> Path:
        """Locates or sets project-level data/raw/ directory."""
        current = Path(__file__).resolve().parent
        for _ in range(4):
            if (current / "corpus").exists() or (current / "docs").exists():
                return current / "data" / "raw"
            current = current.parent
        return Path("data/raw").resolve()

    def fetch_url(self, url: str, timeout: int = 20, max_retries: int = 3) -> str:
        """
        Fetches raw HTML string from target URL with exponential backoff.
        Strictly rejects unwhitelisted URLs.
        """
        if not self.registry.is_url_allowed(url):
            raise PermissionError(
                f"Security Refusal: URL '{url}' is NOT in the approved whitelist of 5 Groww URLs."
            )

        last_exception = None
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Fetching [Attempt {attempt}/{max_retries}]: {url}")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                
                # Check for minimum reasonable HTML length
                if len(response.text) < 1000:
                    raise ValueError(f"Received suspiciously short response ({len(response.text)} bytes).")
                
                return response.text

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < max_retries:
                    sleep_sec = 2 ** attempt
                    logger.info(f"Waiting {sleep_sec}s before retry...")
                    time.sleep(sleep_sec)

        raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_exception}")

    def fetch_and_save_scheme(self, scheme_id: str, force_refresh: bool = False) -> Path:
        """Fetches and persists raw HTML snapshot for a given scheme ID."""
        scheme = self.registry.get_by_id(scheme_id)
        if not scheme:
            raise ValueError(f"Unknown scheme ID: '{scheme_id}'. Must be one of registered 5 schemes.")

        html_file = self.raw_data_dir / f"{scheme_id}.html"
        meta_file = self.raw_data_dir / f"{scheme_id}_meta.json"

        if html_file.exists() and not force_refresh:
            logger.info(f"Using cached raw snapshot: {html_file.name}")
            return html_file

        html_content = self.fetch_url(scheme.source_url)
        crawl_timestamp = datetime.now(timezone.utc).isoformat()

        # Save HTML snapshot
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save crawl metadata snapshot
        meta_data = {
            "scheme_id": scheme.scheme_id,
            "canonical_name": scheme.canonical_name,
            "source_url": scheme.source_url,
            "crawl_timestamp_utc": crawl_timestamp,
            "content_length_bytes": len(html_content),
            "status": "CACHED_SUCCESS"
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2)

        logger.info(f"Successfully cached snapshot for {scheme_id} ({len(html_content)} bytes)")
        return html_file

    def fetch_all(self, delay_seconds: float = 1.5, force_refresh: bool = False) -> Dict[str, Path]:
        """Fetches and caches snapshots for all 5 registered schemes with polite delays."""
        results = {}
        schemes = self.registry.get_all()
        logger.info(f"Starting crawl for all {len(schemes)} whitelisted schemes...")

        for idx, scheme in enumerate(schemes, start=1):
            path = self.fetch_and_save_scheme(scheme.scheme_id, force_refresh=force_refresh)
            results[scheme.scheme_id] = path
            if idx < len(schemes):
                time.sleep(delay_seconds)

        logger.info("✓ Completed crawl for all schemes.")
        return results


if __name__ == "__main__":
    fetcher = SchemeFetcher()
    fetcher.fetch_all(force_refresh=True)
