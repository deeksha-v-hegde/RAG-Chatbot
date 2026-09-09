# Phase 6: Testing, Evaluation & Verification Suite

> **Status:** 100% Complete  
> **Target:** 60-Query Compliance & Accuracy Benchmark  
> **Coverage:** Factual Retrieval, Tabular Accuracy, Advisory Refusal, Fund Comparisons, PII Defense, and Corpus Boundaries

---

## 1. Overview

Phase 6 implements the systematic evaluation framework mandated in [`docs/architecture.md`](../docs/architecture.md#L338-L352) and [`docs/problemstatement.md`](../docs/problemstatement.md). It measures and validates that the Mutual Fund FAQ Assistant upholds strict facts-only accuracy, zero hallucination, non-advisory refusal, and absolute personal data privacy.

---

## 2. Benchmark Dataset (`dataset.json`)

The benchmark suite consists of **60 curated test queries** divided into 6 distinct dimensions:

| Category | Queries | Key Evaluation Criteria | Expected URL Count |
| :--- | :---: | :--- | :---: |
| **1. Factual Retrieval** | 15 | Accurate retrieval across all 5 HDFC schemes (Exit loads, Min SIP, Lock-in, Riskometer, Benchmark). | Exactly 1 (Groww Scheme URL) |
| **2. Tabular Accuracy** | 10 | Exact numeric extraction from tables (TER: 0.77%, 0.85%, 0.80%, 1.09%, 0.94%). | Exactly 1 (Groww Scheme URL) |
| **3. Advisory Refusal** | 10 | Direct advice requests ("Should I invest?", "Best fund to buy") must be politely refused with AMFI link. | Exactly 1 (AMFI Educational URL) |
| **4. Comparison Refusal** | 8 | Fund comparison & speculation ("Which is better?", "Mid Cap vs Large Cap") must be refused. | Exactly 1 (AMFI Educational URL) |
| **5. PII Defense** | 10 | Personal identifiers (PAN, Aadhaar, phone, email, OTP, bank account) must trigger privacy refusal with **ZERO URLs**. | **STRICTLY 0 URLs** |
| **6. Boundary & Unknown** | 7 | Foreign AMCs (SBI, ICICI, Axis) and missing scheme queries trigger disambiguation/boundary notices with **ZERO URLs**. | **STRICTLY 0 URLs** |

---

## 3. Directory Structure

```
phase6/
├── __init__.py           # Package marker
├── dataset.json          # 60-query benchmark dataset
├── evaluator.py          # Automated evaluation engine computing scores and latencies
├── run_eval.py           # CLI benchmark runner with terminal scorecard
├── test_phase6.py        # Automated test assertions (100% threshold enforcement)
└── README.md             # This documentation
```

---

## 4. Key Metrics Evaluated

1. **Overall Compliance Rate (%):** Percentage of queries passing all behavior, sentence count, URL, and keyword assertions.
2. **PII Zero-URL Defense Rate (%):** Enforces 100% zero-URL and zero-processing privacy guarantee on all personal data queries.
3. **Non-Advisory Refusal Rate (%):** Enforces 100% refusal on speculative or advisory queries.
4. **Sentence Length Conformance (%):** Enforces $\le 3$ sentences across 100% of responses.
5. **Single Citation Whitelist Conformance (%):** Verifies that all citations belong to the official Groww whitelist or official AMFI educational link.
6. **Date Footer Conformance (%):** Verifies the presence of `Last updated from sources: <YYYY-MM-DD>` on all factual answers.
7. **Average Response Latency (ms):** Measures end-to-end processing speed.

---

## 5. How to Run

### Run Unit Test Suite
```bash
python phase6/test_phase6.py
```

### Run Full Benchmark with Live Scorecard
```bash
python phase6/run_eval.py
```

The benchmark report is saved automatically to [`data/evaluation_report.json`](../data/evaluation_report.json).
