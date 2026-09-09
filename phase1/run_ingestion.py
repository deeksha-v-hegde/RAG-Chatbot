"""
Convenience CLI Runner for Phase 1 Ingestion Pipeline
Usage:
    python phase1/run_ingestion.py
    python phase1/run_ingestion.py --force-refresh
    python phase1/run_ingestion.py --validate-only
"""

import sys
from pathlib import Path

# Add phase1.6 to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir / "phase1.6"))

from pipeline import main

if __name__ == "__main__":
    main()
