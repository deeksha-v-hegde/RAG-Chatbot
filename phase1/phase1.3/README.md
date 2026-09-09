# Phase 1.3: DOM Parsing, Semantic Section Extraction & Sanitization

## 1. Overview
Subphase 1.3 parses the cached HTML snapshots and extracts clean, deterministic financial metrics and textual content into structured JSON files (`data/extracted/<scheme_id>.json`).

## 2. Implementation Details
- **Module:** `parser.py` (`SchemeDOMParser` and `ParsedSchemeData` classes)
- **Dual Extraction Engine:**
  - Extracts the authoritative Next.js `__NEXT_DATA__` server-side state payload (`mfServerSideData`) for numeric precision.
  - Extracts and sanitizes DOM narrative sections, stripping scripts, ads, and UI chrome.
- **Extracted Attributes per Scheme:**
  - `expense_ratio` (TER % and float value)
  - `exit_load` (cleaned condition string)
  - `min_sip` (SIP minimum with currency formatting, e.g. ₹100, ₹500 for ELSS)
  - `min_lumpsum` (Initial investment minimum)
  - `riskometer` (Risk rating: Moderately High / Very High)
  - `benchmark` (Underlying index name)
  - `lock_in` (Statutory 3-year lock-in for ELSS; Nil for other equity funds)
  - `fund_managers`, `launch_date`, `tax_implications`, `fund_description`, and `stamp_duty`.

## 3. Extracted Scheme Files in `data/extracted/`
- `hdfc_mid_cap.json`
- `hdfc_flexi_cap.json`
- `hdfc_focused.json`
- `hdfc_elss.json`
- `hdfc_large_cap.json`

## 4. Verification & Testing
Run automated unit tests:
```bash
python phase1/phase1.3/test_parser.py
```
*(All 6 tests passed: extraction of 5 schemes, TER validity, exit load, investment limits, benchmark/riskometer, and ELSS statutory lock-in).*
