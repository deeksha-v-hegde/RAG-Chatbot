# Phase 1.4: Normalized Document Generation & Metadata Tagging

## 1. Overview
Subphase 1.4 converts extracted scheme data into standardized, ingestion-ready documents (`data/processed/<scheme_id>.json` and `<scheme_id>.md`) enriched with immutable metadata and pre-formatted atomic semantic chunks with scheme prefix injection.

## 2. Implementation Details
- **Module:** `normalizer.py` (`SchemeNormalizer` class)
- **Output Artifacts per Scheme:**
  - Standardized JSON record with full metric schema and section dictionary.
  - Formatted Markdown summary with markdown tables and embedded chunk definitions.
  - 6 atomic semantic chunks per scheme with prefix injection (`[Scheme: ... | Topic: ...]`) ready for Phase 2 vector embeddings:
    1. `expense_ratio`
    2. `exit_load`
    3. `investment_limits`
    4. `riskometer_and_benchmark`
    5. `lock_in_period`
    6. `overview_and_tax`

## 3. Normalized Scheme Documents in `data/processed/`
- `hdfc_mid_cap.json` & `hdfc_mid_cap.md`
- `hdfc_flexi_cap.json` & `hdfc_flexi_cap.md`
- `hdfc_focused.json` & `hdfc_focused.md`
- `hdfc_elss.json` & `hdfc_elss.md`
- `hdfc_large_cap.json` & `hdfc_large_cap.md`

## 4. Verification & Testing
Run automated unit tests:
```bash
python phase1/phase1.4/test_normalizer.py
```
*(All 4 tests passed: 5 schemes normalized, metadata whitelisting, chunk structure & topic coverage, and ELSS 3-year statutory lock-in text).*
