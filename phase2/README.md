# Phase 2: Chunking, Indexing & Retrieval Architecture

## 1. Overview
Phase 2 implements the vector indexing and retrieval subsystem for the 5 designated HDFC Mutual Fund scheme pages on Groww. It utilizes a **Topic-Based Atomic Chunking Strategy** and **Entity-Aware Metadata Filtering**.

## 2. Key Architecture Components

### 2.1 Topic-Based Atomic Chunks
Instead of arbitrary token sliding-window chunking, the corpus is divided into **exactly 30 atomic, self-contained chunks** (6 chunks per scheme):
- `<scheme>_ter`: Expense Ratio (TER %) and management fee.
- `<scheme>_exit_load`: Penalty percentages and holding duration conditions.
- `<scheme>_investment_limits`: Minimum SIP and initial lumpsum amounts.
- `<scheme>_risk_benchmark`: SEBI Riskometer rating and NIFTY index benchmark.
- `<scheme>_lock_in`: Statutory 3-year lock-in for ELSS; Nil for other funds.
- `<scheme>_overview`: Fund managers, inception date, investment objective, and tax impact.

Every chunk has zero overlap and is prepended with a scheme prefix header:
`[Scheme: <Canonical Name> (Direct Plan - Growth Option) | Topic: <Topic Name>]`

### 2.2 Indexing Engine (`indexer.py`)
- **Vectorizer:** Sublinear TF-IDF N-gram (unigrams & bigrams) vectorizer tailored for financial terms.
- **Persistence Directory:** `data/index/`
  - `chunks.json`: Complete chunk catalog and metadata.
  - `vectorizer.pkl`: Pickled vectorizer model.
  - `tfidf_matrix.npy`: Dense vector matrix for fast cosine similarity.
  - `index_summary.json`: High-level statistics.

### 2.3 Entity-Aware Retriever (`retriever.py`)
- **Scheme Disambiguation:** If a user asks a metric query (*"What is the exit load?"*) without specifying a fund, it returns a polite disambiguation prompt listing the 5 supported schemes.
- **Boundary Detection:** If an unsupported foreign AMC (e.g., SBI, ICICI, Axis) is queried, returns an out-of-scope boundary notice.
- **Targeted Retrieval:** Pre-filters by `scheme_id` when identified, eliminating cross-scheme metric collision and returning top $k=1$ or $k=2$ matching chunks ($<150$ tokens).

---

## 3. Usage Commands

Build vector index:
```bash
python phase2/run_phase2.py --build-index
```

Execute a query:
```bash
python phase2/run_phase2.py --query "What is the exit load for HDFC Mid Cap?"
```

Run automated tests:
```bash
python phase2/test_indexer.py
python phase2/test_retriever.py
```
