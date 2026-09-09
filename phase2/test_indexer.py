"""
Automated Unit Tests for Phase 2: Chunk Indexer
Module: test_indexer.py
"""

import sys
import unittest
from pathlib import Path

# Add search paths for imports
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from indexer import SchemeChunkIndexer


class TestSchemeChunkIndexer(unittest.TestCase):

    def setUp(self):
        self.indexer = SchemeChunkIndexer()

    def test_load_exact_thirty_chunks(self):
        chunks = self.indexer.load_chunks_from_processed()
        self.assertEqual(len(chunks), 30, "Expected exactly 30 atomic chunks (6 chunks x 5 schemes).")

    def test_build_and_save_index(self):
        info = self.indexer.build_index()
        self.assertEqual(info["total_chunks"], 30)
        self.assertGreater(info["vocab_size"], 50)

        index_path = self.indexer.save_index()
        self.assertTrue((index_path / "chunks.json").exists())
        self.assertTrue((index_path / "vectorizer.pkl").exists())
        self.assertTrue((index_path / "tfidf_matrix.npy").exists())
        self.assertTrue((index_path / "index_summary.json").exists())

    def test_reload_saved_index(self):
        new_indexer = SchemeChunkIndexer()
        new_indexer.load_index()
        self.assertEqual(len(new_indexer.chunks), 30)
        self.assertIsNotNone(new_indexer.vectorizer)
        self.assertEqual(new_indexer.tfidf_matrix.shape[0], 30)


if __name__ == "__main__":
    unittest.main()
