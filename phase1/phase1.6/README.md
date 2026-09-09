# Phase 1.6: Ingestion Pipeline Orchestrator & CLI Runner

## 1. Overview
Subphase 1.6 unifies Subphases 1.1 through 1.5 into an end-to-end executable pipeline with CLI commands, progress logging, and error recovery.

## 2. Pipeline Execution Sequence
1. **Subphase 1.1:** Loads `corpus/sources.json` and verifies the strict 5-scheme whitelist.
2. **Subphase 1.2:** Crawls Groww URLs with exponential backoff and caches raw HTML in `data/raw/`.
3. **Subphase 1.3:** Parses Next.js server-side state and sanitizes DOM sections in `data/extracted/`.
4. **Subphase 1.4:** Normalizes documents into JSON and Markdown, generating 30 atomic semantic chunks with prefix injection in `data/processed/`.
5. **Subphase 1.5:** Runs the compliance audit and writes `data/ingestion_report.json`.

## 3. Usage Commands
Run the complete pipeline:
```bash
python phase1/run_ingestion.py
```

Run with live web re-crawl (bypassing raw HTML cache):
```bash
python phase1/run_ingestion.py --force-refresh
```

Run validation assertions only on existing processed data:
```bash
python phase1/run_ingestion.py --validate-only
```

## 4. Verification & Testing
Run automated unit tests:
```bash
python phase1/phase1.6/test_pipeline.py
```
*(Test passed: End-to-end pipeline run produces status PASSED with 5 schemes, 30 chunks, and audit pass).*
