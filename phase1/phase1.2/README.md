# Phase 1.2: Raw Web Fetching & Snapshot Persistence

## 1. Overview
Subphase 1.2 fetches and persists the raw HTML page snapshots for the 5 whitelisted Groww HDFC mutual fund URLs into `data/raw/<scheme_id>.html` along with metadata snapshots (`<scheme_id>_meta.json`).

## 2. Implementation Details
- **Module:** `fetcher.py` (`SchemeFetcher` class)
- **Strict Whitelist Protection:** Enforces URL validation through `SchemeRegistry`; any non-whitelisted URL raises a `PermissionError`.
- **Anti-Bot & Resilience:** Realistic browser `User-Agent` headers, exponential backoff retries (3 attempts), and minimum content-length assertions.
- **Snapshot Caching:** Saves raw HTML locally to avoid repeated network hits and supports `--force-refresh`.
- **Crawl Metadata:** Stores crawl timestamps (UTC), content sizes, and source URLs.

## 3. Cached Snapshots in `data/raw/`
- `hdfc_mid_cap.html` (~486 KB)
- `hdfc_flexi_cap.html` (~488 KB)
- `hdfc_focused.html` (~433 KB)
- `hdfc_elss.html` (~450 KB)
- `hdfc_large_cap.html` (~449 KB)

## 4. Verification & Testing
Run automated unit tests:
```bash
python phase1/phase1.2/test_fetcher.py
```
*(All 3 tests passed: whitelist refusal, fetch & cache integrity, and cache reuse).*
