"""
Phase 2: Chunking, Indexing & Retrieval Architecture
Module: retriever.py

Implements entity-aware metadata-filtered retrieval, disambiguation routing,
and out-of-corpus boundary detection over the 30 atomic scheme chunks.
"""

import re
import logging
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import sys
# Add search paths for phase1 and phase2 modules
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))

from registry import SchemeRegistry, SchemeSource
from indexer import SchemeChunkIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase2_Retriever")

# Common foreign AMCs to detect out-of-corpus queries
FOREIGN_AMCS = [
    "sbi", "icici", "axis", "nippon", "kotak", "mirae", "parag parikh",
    "quant", "tata", "uti", "aditya birla", "dsp", "motilal oswal"
]

# Topic keyword mappings for intent identification
TOPIC_KEYWORDS = {
    "expense_ratio": ["expense ratio", "ter", "total expense", "management fee", "annual fee", "charges", "fees", "cost"],
    "exit_load": ["exit load", "penalty", "redemption charge", "exit fee", "redeeming charge", "exit charges", "load"],
    "investment_limits": ["minimum sip", "min sip", "sip amount", "minimum investment", "lumpsum", "min lumpsum", "min amount"],
    "riskometer_and_benchmark": [
        "riskometer", "risk rating", "risk category", "risk level", "risk", "riskometer rating",
        "benchmark", "benchmark index", "index", "riskometer level", "risk profile", "moderately high", "very high"
    ],
    "lock_in_period": ["lock in", "lock-in", "lockin", "mandatory lock", "statutory lock", "3 years lock", "elss lock"],
    "overview_and_tax": ["fund manager", "managed by", "launch date", "inception", "stamp duty", "tax", "taxation", "history", "launch", "when was", "started"],
}


@dataclass
class RetrievalResult:
    query: str
    target_scheme_id: Optional[str] = None
    target_scheme_name: Optional[str] = None
    target_topic: Optional[str] = None
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    top_chunk: Optional[Dict[str, Any]] = None
    top_score: float = 0.0
    is_disambiguation: bool = False
    is_unsupported_scheme: bool = False
    status_message: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SchemeRetriever:
    """Performs metadata-filtered vector search and intent-aware routing over the 30 atomic chunks."""

    def __init__(self, indexer: Optional[SchemeChunkIndexer] = None):
        self.indexer = indexer or SchemeChunkIndexer()
        self.indexer.load_index()
        self.registry = self.indexer.registry

    def detect_unsupported_scheme(self, query: str) -> Optional[str]:
        """Detects if query mentions a foreign non-HDFC mutual fund."""
        query_lower = query.lower()
        for amc in FOREIGN_AMCS:
            if re.search(rf"\b{re.escape(amc)}\b", query_lower):
                # Ensure it's not mentioning HDFC
                if "hdfc" not in query_lower:
                    return amc.upper()
        return None

    def detect_topic(self, query: str) -> Optional[str]:
        """Infers the financial metric topic being inquired about."""
        query_lower = query.lower()
        for topic, keywords in TOPIC_KEYWORDS.items():
            for kw in keywords:
                if len(kw) <= 4:
                    if re.search(rf"\b{re.escape(kw)}\b", query_lower):
                        return topic
                else:
                    if kw in query_lower:
                        return topic
        return None

    def retrieve(self, query: str, top_k: int = 1) -> RetrievalResult:
        """
        Executes entity-aware similarity retrieval:
        1. Checks for out-of-corpus foreign schemes.
        2. Resolves scheme identity from query.
        3. Flags ambiguous queries missing scheme context.
        4. Performs cosine similarity search over matching chunks.
        """
        query_clean = query.strip()
        if not query_clean:
            return RetrievalResult(
                query=query,
                status_message="EMPTY_QUERY",
            )

        # 1. Check for foreign AMC
        foreign_amc = self.detect_unsupported_scheme(query_clean)
        if foreign_amc:
            return RetrievalResult(
                query=query_clean,
                is_unsupported_scheme=True,
                status_message=(
                    f"Out of Scope: Query refers to {foreign_amc}. "
                    "This assistant only answers factual queries for the 5 designated HDFC Mutual Fund schemes on Groww."
                ),
            )

        # 2. Resolve Scheme Entity
        scheme = self.registry.resolve_scheme_from_query(query_clean)
        topic = self.detect_topic(query_clean)

        # 3. Disambiguation Check: Metric asked, but no scheme specified
        if not scheme and topic:
            supported_schemes = [
                f"{s.canonical_name}" for s in self.registry.get_all()
            ]
            msg = (
                "Please specify which HDFC fund you are asking about: "
                + ", ".join(supported_schemes)
                + "."
            )
            return RetrievalResult(
                query=query_clean,
                target_topic=topic,
                is_disambiguation=True,
                status_message=msg,
            )

        # 4. Filter candidate chunks based on resolved scheme
        candidate_indices = []
        candidate_chunks = []

        target_scheme_id = scheme.scheme_id if scheme else None
        target_scheme_name = scheme.canonical_name if scheme else None

        for idx, chunk in enumerate(self.indexer.chunks):
            if target_scheme_id:
                if chunk["scheme_id"] == target_scheme_id:
                    candidate_indices.append(idx)
                    candidate_chunks.append(chunk)
            else:
                candidate_indices.append(idx)
                candidate_chunks.append(chunk)

        if not candidate_chunks:
            return RetrievalResult(
                query=query_clean,
                status_message="NO_CANDIDATE_CHUNKS",
            )

        # 5. Vectorize Query and Compute Cosine Similarity
        query_vec = self.indexer.vectorizer.transform([query_clean]).toarray()
        candidate_matrix = self.indexer.tfidf_matrix[candidate_indices]
        base_scores = cosine_similarity(query_vec, candidate_matrix)[0]

        # 5b. Apply Topic & Keyword Intent Weighting
        query_lower = query_clean.lower()
        adjusted_scores = []
        for idx, chunk in enumerate(candidate_chunks):
            s = float(base_scores[idx])
            chunk_topic = chunk.get("topic", "")

            # Strong boost if detected query topic matches chunk topic
            if topic and chunk_topic == topic:
                s += 0.50

            # Direct keyword intent boosts
            if any(k in query_lower for k in ["risk", "riskometer", "benchmark"]):
                if chunk_topic == "riskometer_and_benchmark":
                    s += 0.60
            if any(k in query_lower for k in ["exit load", "penalty", "redeem", "redemption"]):
                if chunk_topic == "exit_load":
                    s += 0.60
            if any(k in query_lower for k in ["expense", "management fee", "charges", "annual fee"]) or re.search(r"\bter\b", query_lower):
                if chunk_topic == "expense_ratio":
                    s += 0.60
            if any(k in query_lower for k in ["lock in", "lock-in", "lockin"]):
                if chunk_topic == "lock_in_period":
                    s += 0.60
            if any(k in query_lower for k in ["sip", "lumpsum", "minimum"]):
                if chunk_topic == "investment_limits":
                    s += 0.60
            if any(k in query_lower for k in ["launch", "inception", "founded", "history", "tax", "stamp duty", "when was"]):
                if chunk_topic == "overview_and_tax":
                    s += 0.60

            adjusted_scores.append(s)

        scores = np.array(adjusted_scores)

        # 6. Rank Results
        ranked_indices = np.argsort(scores)[::-1]
        top_k = min(top_k, len(candidate_chunks))

        ranked_results = []
        for i in range(top_k):
            match_idx = ranked_indices[i]
            chunk_data = dict(candidate_chunks[match_idx])
            chunk_data["score"] = float(scores[match_idx])
            ranked_results.append(chunk_data)

        top_chunk = ranked_results[0] if ranked_results else None
        top_score = top_chunk["score"] if top_chunk else 0.0

        return RetrievalResult(
            query=query_clean,
            target_scheme_id=target_scheme_id,
            target_scheme_name=target_scheme_name,
            target_topic=topic,
            chunks=ranked_results,
            top_chunk=top_chunk,
            top_score=top_score,
            is_disambiguation=False,
            is_unsupported_scheme=False,
            status_message="SUCCESS",
        )


if __name__ == "__main__":
    retriever = SchemeRetriever()
    test_queries = [
        "What is the exit load for HDFC Mid Cap?",
        "Tell me the expense ratio of HDFC Flexicap",
        "What is the lock in period for HDFC ELSS?",
        "What is the exit load?",  # Ambiguous
        "What is the expense ratio of SBI Small Cap?",  # Unsupported
    ]
    print("\n--- Running Sample Retrievals ---")
    for q in test_queries:
        res = retriever.retrieve(q, top_k=1)
        print(f"\nQuery: '{q}'")
        print(f"Status: {res.status_message}")
        if res.top_chunk:
            print(f"Match [{res.top_chunk['chunk_id']}] (Score: {res.top_score:.3f})")
            print(f"Text: {res.top_chunk['text'][:120]}...")
