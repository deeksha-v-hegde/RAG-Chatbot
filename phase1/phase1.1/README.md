# Phase 1.1: Corpus Definition & Sources Whitelist Registry

## 1. Overview
Subphase 1.1 formalizes the single source of truth for the 5 authorized HDFC Mutual Fund scheme pages on Groww. It defines the strict URL whitelist, metadata schema, and entity resolver.

## 2. Whitelisted Scheme Inventory

| Scheme ID | Canonical Name | Target URL | Category |
| :--- | :--- | :--- | :--- |
| `hdfc_mid_cap` | HDFC Mid-Cap Opportunities Fund | `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth` | Equity - Mid Cap |
| `hdfc_flexi_cap` | HDFC Flexi Cap Fund | `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth` | Equity - Flexi Cap |
| `hdfc_focused` | HDFC Focused 30 Fund | `https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth` | Equity - Focused |
| `hdfc_elss` | HDFC ELSS Tax Saver Fund | `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth` | Equity - ELSS (3-yr Lock-in) |
| `hdfc_large_cap` | HDFC Top 100 Fund | `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` | Equity - Large Cap |

## 3. Files in this Directory
- `registry.py`: Core `SchemeRegistry` class, `SchemeSource` dataclass, and strict whitelist validation logic.
- `test_registry.py`: Unit test suite ensuring exact 5-scheme loading, whitelist rejection, and alias resolution.
- `corpus/sources.json`: Canonical registry JSON file located at project root.

## 4. How to Verify
Run the automated test suite:
```bash
python phase1/phase1.1/test_registry.py
```
