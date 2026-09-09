# Phase 1.5: Ingestion Validation & Integrity Verification

## 1. Overview
Subphase 1.5 performs automated sanity and regulatory compliance assertions on all processed documents in `data/processed/`, certifying that the corpus is complete, accurate, and ready for Phase 2 vector indexing.

## 2. Implementation Details
- **Module:** `validator.py` (`IngestionValidator` class)
- **Automated Audit Checks:**
  - Whitelist assertion: Confirms all source URLs match the 5 approved Groww URLs.
  - Presence check: Confirms exactly 5 `.json` and 5 `.md` files exist.
  - Metric non-null assertions: TER %, Exit load string, Min SIP ($\ge ₹100$), Riskometer, and Benchmark.
  - ELSS compliance: Explicit assertion that `hdfc_elss` has statutory lock-in set to exactly 3 years.
  - Chunks check: Confirms $\ge 6$ structured semantic chunks per scheme with prefix injection.
- **Audit Report:** Generated at [`data/ingestion_report.json`](file:///c:/Users/Admin/Projects/RAG%20Chatbot/data/ingestion_report.json).

## 3. Verification & Testing
Run automated unit tests:
```bash
python phase1/phase1.5/test_validator.py
```
*(All 3 tests passed: 100% audit pass, report file generation, and all 5 schemes validated).*
