"""
Phase 1.1: Corpus Definition & Sources Whitelist Registry
Module: registry.py

Defines the scheme data structures, strict URL whitelist, and canonical registry
for the 5 designated HDFC Mutual Fund schemes on Groww.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Set


# Strict Whitelist of Approved URLs (No other URLs are permitted)
WHITELISTED_URLS: Set[str] = {
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
}


@dataclass
class SchemeSource:
    scheme_id: str
    canonical_name: str
    plan_type: str
    category: str
    source_url: str
    citation_title: str
    expected_metrics: List[str]
    aliases: List[str] = field(default_factory=list)
    statutory_lock_in_years: Optional[int] = None

    def validate(self) -> None:
        """Validates that the scheme source adheres to the strict whitelist rules."""
        if self.source_url not in WHITELISTED_URLS:
            raise ValueError(
                f"URL '{self.source_url}' is NOT in the approved whitelist of 5 designated Groww URLs."
            )
        if not self.scheme_id:
            raise ValueError("Scheme ID cannot be empty.")
        if not self.canonical_name:
            raise ValueError("Canonical name cannot be empty.")


class SchemeRegistry:
    """Manages the catalog of supported HDFC mutual fund schemes and enforces whitelist constraints."""

    def __init__(self, sources_file: Optional[Path] = None):
        self.sources_file = sources_file or self._find_sources_file()
        self._schemes_by_id: Dict[str, SchemeSource] = {}
        self._schemes_by_url: Dict[str, SchemeSource] = {}
        self.load()

    @staticmethod
    def _find_sources_file() -> Path:
        """Locates the corpus/sources.json path relative to project root."""
        # Check current working directory
        cwd_path = Path("corpus/sources.json").resolve()
        if cwd_path.exists():
            return cwd_path
        # Traverse parent directories
        current = Path(__file__).resolve().parent
        for _ in range(4):
            candidate = current / "corpus" / "sources.json"
            if candidate.exists():
                return candidate
            candidate_root = current.parent / "corpus" / "sources.json"
            if candidate_root.exists():
                return candidate_root
            current = current.parent
        return cwd_path

    def load(self) -> None:
        """Loads and validates all scheme definitions from sources.json."""
        if not self.sources_file.exists():
            raise FileNotFoundError(
                f"Registry configuration file not found at: {self.sources_file}"
            )

        with open(self.sources_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        raw_schemes = data.get("schemes", [])
        if len(raw_schemes) != 5:
            raise ValueError(
                f"Expected exactly 5 schemes in registry, but found {len(raw_schemes)}."
            )

        self._schemes_by_id.clear()
        self._schemes_by_url.clear()

        for item in raw_schemes:
            scheme = SchemeSource(
                scheme_id=item["scheme_id"],
                canonical_name=item["canonical_name"],
                plan_type=item.get("plan_type", "Direct Plan - Growth Option"),
                category=item["category"],
                source_url=item["source_url"],
                citation_title=item["citation_title"],
                expected_metrics=item.get("expected_metrics", []),
                aliases=item.get("aliases", []),
                statutory_lock_in_years=item.get("statutory_lock_in_years"),
            )
            scheme.validate()
            self._schemes_by_id[scheme.scheme_id] = scheme
            self._schemes_by_url[scheme.source_url] = scheme

    def is_url_allowed(self, url: str) -> bool:
        """Checks if a given URL is strictly within the approved whitelist."""
        return url in WHITELISTED_URLS

    def get_by_id(self, scheme_id: str) -> Optional[SchemeSource]:
        """Returns scheme record by canonical scheme ID."""
        return self._schemes_by_id.get(scheme_id)

    def get_by_url(self, url: str) -> Optional[SchemeSource]:
        """Returns scheme record by source URL."""
        return self._schemes_by_url.get(url)

    def get_all(self) -> List[SchemeSource]:
        """Returns all 5 registered schemes."""
        return list(self._schemes_by_id.values())

    def resolve_scheme_from_query(self, query: str) -> Optional[SchemeSource]:
        """
        Resolves which scheme the user query is asking about using canonical names and aliases.
        Returns None if ambiguous or unspecified.
        """
        query_lower = query.lower()
        query_norm = query_lower.replace("-", " ")
        matched: List[SchemeSource] = []

        for scheme in self.get_all():
            # Check canonical name
            canonical_norm = scheme.canonical_name.lower().replace("-", " ")
            if canonical_norm in query_norm or scheme.canonical_name.lower() in query_lower:
                matched.append(scheme)
                continue
            # Check aliases
            for alias in scheme.aliases:
                alias_norm = alias.lower().replace("-", " ")
                if alias_norm in query_norm or alias.lower() in query_lower:
                    matched.append(scheme)
                    break

        # If exactly one scheme matches, return it
        if len(matched) == 1:
            return matched[0]
        # Ambiguous or no match
        return None

    def export_summary(self) -> dict:
        """Returns a serializable dictionary summary of the registered schemes."""
        return {
            "total_registered": len(self._schemes_by_id),
            "whitelisted_urls": list(WHITELISTED_URLS),
            "schemes": [asdict(s) for s in self.get_all()],
        }


if __name__ == "__main__":
    registry = SchemeRegistry()
    print("✓ SchemeRegistry loaded successfully:")
    for s in registry.get_all():
        print(f"  [{s.scheme_id}] {s.canonical_name} -> {s.source_url}")
