"""
CLI Runner for Phase 2: Indexer and Retriever
Usage:
    python phase2/run_phase2.py --build-index
    python phase2/run_phase2.py --query "What is the exit load for HDFC Mid Cap?"
"""

import sys
import argparse
from pathlib import Path

# Add search path for phase2 modules
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from indexer import SchemeChunkIndexer
from retriever import SchemeRetriever


def main():
    parser = argparse.ArgumentParser(description="Phase 2: Indexing & Retrieval Runner")
    parser.add_argument("--build-index", action="store_true", help="Build and save the vector index.")
    parser.add_argument("--query", type=str, help="Execute sample retrieval for a query.")

    args = parser.parse_args()

    if args.build_index or not args.query:
        print("\n>>> Building Vector Index from data/processed/...")
        indexer = SchemeChunkIndexer()
        indexer.build_index()
        indexer.save_index()
        print("[SUCCESS] Index build complete.")

    if args.query:
        print(f"\n>>> Executing Retrieval for query: '{args.query}'")
        retriever = SchemeRetriever()
        res = retriever.retrieve(args.query, top_k=2)
        print(f"Status: {res.status_message}")
        if res.is_disambiguation:
            print(f"Disambiguation Note: {res.status_message}")
        elif res.is_unsupported_scheme:
            print(f"Boundary Notice: {res.status_message}")
        elif res.top_chunk:
            print(f"Top Matched Chunk: [{res.top_chunk['chunk_id']}] (Score: {res.top_score:.3f})")
            print(f"Topic: {res.top_chunk['topic']}")
            print(f"Source URL: {res.top_chunk['source_url']}")
            print(f"Last Updated: {res.top_chunk['last_updated']}")
            print("\nRetrieved Passage:")
            print("-" * 50)
            print(res.top_chunk["text"])
            print("-" * 50)


if __name__ == "__main__":
    main()
