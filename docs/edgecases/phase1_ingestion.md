# Phase 1 Edge Cases: Corpus Curation & Ingestion Pipeline

> **Scope:** Web Scraping, HTML/DOM Parsing, and Metadata Extraction from the 5 designated Groww HDFC URLs.

---

## 1. Overview of Phase 1 Risks

In Phase 1, data is collected exclusively from 5 Groww URLs representing HDFC mutual fund schemes:
1. `https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth`
2. `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth` (HDFC Flexi Cap)
3. `https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth` (HDFC Focused 30)
4. `https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth` (HDFC ELSS Tax Saver)
5. `https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth` (HDFC Top 100 / Large Cap)

Since Groww is a client-rendered React/Next.js single-page application with dynamic hydration and periodically changing DOM classes, raw HTTP `GET` requests and rigid selectors can easily break or produce empty scrapes.

---

## 2. Detailed Edge Cases & Failure Modes

### Edge Case 1.1: Client-Side Rendering (CSR) & Empty HTML Bodies
- **Scenario:** The ingestion scraper executes a simple `requests.get()` or `urllib.request()`, receiving a static HTML shell where mutual fund details are rendered client-side via JavaScript.
- **Failure Mode:** Extracted text is empty or only contains `<div id="__next"></div>` and script tags. The vector store indexes empty strings.
- **Detection:** Page content length `< 500` characters or absence of critical keywords like "Expense Ratio" or "Exit Load".
- **Mitigation Strategy:**
  - Use headless rendering (e.g., Playwright, Puppeteer, or Selenium) or extract pre-rendered initial state JSON from `<script id="__NEXT_DATA__">`.
  - Validate that required fields (scheme name, expense ratio, minimum SIP) are non-null before committing to the parsed document registry.

---

### Edge Case 1.2: DOM Layout / Class Name Drift
- **Scenario:** Groww updates its frontend build, causing CSS modules or Tailwind class names (e.g., `.fs14.clrText`) to change hashes.
- **Failure Mode:** Hardcoded CSS/XPath selectors fail silently, returning `None` or selecting irrelevant elements (e.g., footer links).
- **Detection:** Selector extraction yields empty results for critical data fields.
- **Mitigation Strategy:**
  - Avoid brittle CSS class selectors (e.g., `.css-19f8x9`).
  - Use semantic text-anchored extraction: locate label text `"Expense ratio"`, `"Exit load"`, `"Lock-in period"`, or `"Minimum SIP"`, and traverse to adjacent sibling or parent elements.
  - Fallback to full-page markdown conversion via `trafilatura` or `html2text`, filtering by section headers.

---

### Edge Case 1.3: Anti-Scraping Triggers, Cloudflare / Bot Protection, and 403 Forbidden
- **Scenario:** Rapid sequential requests trigger Cloudflare, rate limits (HTTP 429), or bot blocking (HTTP 403 / 503).
- **Failure Mode:** Ingestion pipeline crashes or stores CAPTCHA challenge pages as scheme content.
- **Detection:** HTTP status codes $\ge 400$, response containing phrases like `"Verify you are human"`, `"Access Denied"`, or `"Cloudflare"`.
- **Mitigation Strategy:**
  - Set realistic browser User-Agent headers, accept-language, and standard headers.
  - Add polite jitter/delays ($2-5$ seconds) between requests (only 5 URLs need to be fetched).
  - Cache raw downloaded HTML locally (`data/raw/`) to eliminate repeated network fetches during development.

---

### Edge Case 1.4: Incomplete / Stale Scheme Data (e.g., "N/A" or "Data Awaited")
- **Scenario:** A metric field on the webpage displays "—", "N/A", or is temporarily blank (e.g., during monthly portfolio rebalancing updates).
- **Failure Mode:** RAG pipeline indexes "Expense ratio: —", and subsequently answers queries with unhelpful or missing data.
- **Detection:** Schema validation regex flagging dashes or `"N/A"` on mandatory fields.
- **Mitigation Strategy:**
  - Raise an ingestion warning if core attributes (TER, Exit Load, Lock-in) are missing or null.
  - Record the exact crawl timestamp (`last_updated`) to ensure transparency on when the data was retrieved.

---

### Edge Case 1.5: Inconsistent Plan Disclosures (Direct vs. Regular Plans)
- **Scenario:** Groww page contains information for both Direct-Growth and Regular plans or switches between tabs.
- **Failure Mode:** Assistant extracts Regular plan expense ratio (e.g., $1.75\%$) instead of Direct plan ($0.85\%$).
- **Detection:** Verification that extracted plan metadata explicitly matches `"Direct"` and `"Growth"`.
- **Mitigation Strategy:**
  - Explicitly filter and tag all chunks with plan type `Plan: Direct - Growth`.
  - Prepend explicit disambiguation text to each chunk: `Scheme: [Scheme Name] (Direct Plan - Growth Option)`.

---

## 3. Ingestion Validation Checklist

| Check | Requirement | Enforced By |
| :--- | :--- | :--- |
| **URL Whitelist Check** | URL must be one of the 5 approved Groww URLs | Hardcoded URL enum check |
| **Payload Integrity** | Contains Scheme Name, Expense Ratio, Min SIP, Exit Load | Pre-indexing schema validator |
| **Content Size** | Extracted text $> 1,000$ characters per page | Length assertion check |
| **Local Snapshot** | Raw HTML cached in `corpus/raw/` with UTC timestamp | File snapshot logger |
