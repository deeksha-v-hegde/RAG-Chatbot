"""
Phase 2: Chunking, Indexing & Retrieval Architecture
Module: indexer.py

Loads the 30 atomic semantic chunks from data/processed/ and builds a persistent
local vector and keyword index with metadata filters.
"""

import os
import sys
import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# Ensure phase1 modules can be imported
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))

from registry import SchemeRegistry, WHITELISTED_URLS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase2_Indexer")


class SchemeChunkIndexer:
    """Manages creation, vectorization, and storage of atomic semantic chunks."""

    def __init__(
        self,
        processed_dir: Optional[Path] = None,
        index_dir: Optional[Path] = None,
        registry: Optional[SchemeRegistry] = None,
    ):
        self.project_root = project_root
        self.processed_dir = processed_dir or (self.project_root / "data" / "processed")
        self.index_dir = index_dir or (self.project_root / "data" / "index")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry or SchemeRegistry()

        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[np.ndarray] = None

    def load_chunks_from_processed(self) -> List[Dict[str, Any]]:
        """Loads and flattens all atomic chunks from processed scheme JSON files."""
        all_chunks = []
        scheme_files = list(self.processed_dir.glob("*.json"))

        if not scheme_files:
            raise FileNotFoundError(
                f"No processed scheme JSON files found in: {self.processed_dir}. Run Phase 1 first."
            )

        for s_file in sorted(scheme_files):
            with open(s_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            scheme_chunks = data.get("structured_chunks", [])
            for c in scheme_chunks:
                # Ensure source_url is whitelisted
                if c.get("source_url") not in WHITELISTED_URLS:
                    raise ValueError(f"Chunk contains unapproved URL: {c.get('source_url')}")
                all_chunks.append(c)

        self.chunks = all_chunks
        logger.info(f"Loaded {len(self.chunks)} atomic semantic chunks from {len(scheme_files)} schemes.")
        return self.chunks

    def build_index(self) -> Dict[str, Any]:
        """Fits TF-IDF vectorizer and produces normalized dense feature vectors."""
        if not self.chunks:
            self.load_chunks_from_processed()

        if len(self.chunks) != 30:
            logger.warning(f"Expected exactly 30 atomic chunks (6x5), found {len(self.chunks)}")

        corpus_texts = [c["text"] for c in self.chunks]

        # Fit sublinear TF-IDF with unigrams and bigrams for financial phrases
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            stop_words="english",
            lowercase=True,
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts).toarray()

        logger.info(
            f"Built vector index with shape {self.tfidf_matrix.shape} (vocab: {len(self.vectorizer.vocabulary_)})"
        )
        return {
            "total_chunks": len(self.chunks),
            "vocab_size": len(self.vectorizer.vocabulary_),
            "matrix_shape": list(self.tfidf_matrix.shape),
        }

    def save_index(self) -> Path:
        """Persists the chunks registry, vectorizer, and matrix to data/index/."""
        if self.vectorizer is None or self.tfidf_matrix is None:
            self.build_index()

        # 1. Save chunks metadata
        chunks_file = self.index_dir / "chunks.json"
        with open(chunks_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)

        # 2. Save vectorizer model
        vectorizer_file = self.index_dir / "vectorizer.pkl"
        with open(vectorizer_file, "wb") as f:
            pickle.dump(self.vectorizer, f)

        # 3. Save matrix
        matrix_file = self.index_dir / "tfidf_matrix.npy"
        np.save(matrix_file, self.tfidf_matrix)

        # 4. Save index summary
        summary_file = self.index_dir / "index_summary.json"
        summary_data = {
            "total_schemes": 5,
            "total_chunks": len(self.chunks),
            "chunks_per_scheme": len(self.chunks) // 5 if len(self.chunks) else 0,
            "vocab_size": len(self.vectorizer.vocabulary_),
            "embedding_type": "TF-IDF Sublinear N-gram Vectors (Local)",
            "index_files": [
                chunks_file.name,
                vectorizer_file.name,
                matrix_file.name,
            ],
        }
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        logger.info(f"✓ Index successfully persisted to {self.index_dir}")
        return self.index_dir

    def load_index(self) -> None:
        """Loads a pre-built index from disk."""
        chunks_file = self.index_dir / "chunks.json"
        vectorizer_file = self.index_dir / "vectorizer.pkl"
        matrix_file = self.index_dir / "tfidf_matrix.npy"

        if not chunks_file.exists() or not vectorizer_file.exists() or not matrix_file.exists():
            logger.info("Existing index not found. Building fresh index from processed data...")
            self.build_index()
            self.save_index()
            return

        with open(chunks_file, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        with open(vectorizer_file, "rb") as f:
            self.vectorizer = pickle.load(f)

        self.tfidf_matrix = np.load(matrix_file)
        logger.info(f"Loaded existing index ({len(self.chunks)} chunks) from disk.")


if __name__ == "__main__":
    indexer = SchemeChunkIndexer()
    indexer.build_index()
    indexer.save_index()
