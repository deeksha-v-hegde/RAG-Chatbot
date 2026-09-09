# Phase 4: Groq LLM & RAG Output Synthesis

> **Status:** 100% Complete  
> **Compliance Standard:** Strictly Facts-Only, Non-Advisory, Deterministic Output Format  
> **LLM Engine:** Groq Cloud API (`llama-3.3-70b-versatile` / `llama-3.1-8b-instant`) at `temperature = 0.0`

---

## 1. Overview

Phase 4 implements the end-to-end Retrieval-Augmented Generation (RAG) synthesis and post-validation layer as specified in [`docs/architecture.md`](../docs/architecture.md). It wires together:
1. **Phase 3 Guardrails:** Intercepts PII, advisory queries, fund comparisons, and jailbreaks.
2. **Phase 2 Entity-Gated Retrieval:** Fetches the single top-1 atomic passage ($<100$ context tokens) eliminating cross-scheme collision.
3. **Phase 4 Groq LLM Engine:** Zero-temperature prompt execution using `llama-3.3-70b-versatile` (with graceful fallback to `llama-3.1-8b-instant` and deterministic grounded offline mode).
4. **Phase 4 Output Post-Validation Layer:** Enforces regulatory formatting constraints ($\le 3$ sentences, strictly 1 citation URL on verified facts, strictly 0 URLs on unknown/PII queries, and the mandatory `Last updated from sources: <date>` footer).

---

## 2. Directory Structure

```
phase4/
├── __init__.py               # Package initializer
├── prompt_templates.py       # Strict system prompt and RAG context assembler
├── groq_client.py            # Groq API client with temperature=0.0 and offline fallback
├── post_validator.py         # Layer 4.2: Sentence limiter & strict No-URL validator
├── synthesizer.py            # Master RAG orchestrator connecting Phases 1, 2, 3, & 4
├── run_phase4.py             # CLI runner for single query, demo suite, or interactive chat
├── test_phase4.py            # Comprehensive unit test suite (9/9 tests passing)
└── README.md                 # This documentation
```

---

## 3. Key Modules & Design

### 3.1 Prompt Templates (`prompt_templates.py`)
- **Deterministic Behavior:** Instructs the model to rely solely on the provided chunk without extrapolating or speculating.
- **Strict Format Enforced:**
  - Length: Maximum 3 sentences.
  - Known Facts: Exactly 1 markdown citation link + `Last updated from sources: <YYYY-MM-DD>`.
  - Unknown Facts: Explicit statement that information is unavailable and **STRICTLY NO URL**.
  - PII Queries: **STRICTLY NO URL** and immediate security notice.

### 3.2 Groq LLM Client (`groq_client.py`)
- **Primary Model:** `llama-3.3-70b-versatile`
- **Fallback Model:** `llama-3.1-8b-instant`
- **Zero-Temperature Mode:** `temperature=0.0` ensures reproducible, deterministic factual output.
- **Offline Grounded Fallback:** When `GROQ_API_KEY` is not present or if the network is unavailable, the client executes deterministic extraction directly from the verified atomic chunk, allowing 100% offline testing and high-availability execution.

### 3.3 Output Post-Validator (`post_validator.py`)
- **Sentence Limiter:** Truncates responses exceeding 3 sentences to comply with the 3-sentence mandate.
- **Strict URL Rules:**
  - **Factual Answers:** Enforces exactly 1 whitelisted URL matching the canonical scheme.
  - **Unknown Answers:** Verifies that exactly **0 URLs** are present.
  - **Personal Information (PII):** Verifies that exactly **0 URLs** are attached.
- **Timestamp Footer:** Guarantees `Last updated from sources: <YYYY-MM-DD>` is present on factual answers.

### 3.4 Master Synthesizer (`synthesizer.py`)
Orchestrates the entire query lifecycle:
```
User Query
    │
    ▼
Phase 3 Guardrails (PII / Advisory Check)
    ├── [PII Detected] ───────────────► Security Notice (0 URLs)
    ├── [Advisory / Comparison] ──────► Refusal + AMFI Education Link
    └── [Clean Factual Query]
            │
            ▼
Phase 2 Entity-Gated Retrieval
    ├── [Foreign AMC] ────────────────► Out-of-Scope Notice (0 URLs)
    ├── [Missing Scheme] ─────────────► Disambiguation Prompt (0 URLs)
    └── [Resolved Scheme]
            │
            ▼
Phase 4 Groq LLM Synthesis (temp=0.0)
            │
            ▼
Phase 4 Post-Validation & Normalization (<= 3 sentences, 1 URL, footer)
            │
            ▼
Verified Final Response
```

---

## 4. How to Run

### Run Unit Tests
```bash
python phase4/test_phase4.py
```
*Expected Output: `Ran 9 tests ... OK`*

### Run Batch Demo
```bash
python phase4/run_phase4.py
```

### Run Single Query
```bash
python phase4/run_phase4.py --query "What is the exit load for HDFC Mid Cap?"
```

### Run Interactive Chat Mode
```bash
python phase4/run_phase4.py --interactive
```

---

## 5. Setting up Groq API Key (Optional)

To enable live cloud LLM generation via Groq:
1. Obtain an API key from [Groq Console](https://console.groq.com/).
2. Set the environment variable:
   ```powershell
   $env:GROQ_API_KEY="gsk_..."
   ```
   Or add it to a `.env` file in the project root:
   ```
   GROQ_API_KEY=gsk_...
   ```
If no key is provided, Phase 4 automatically operates in deterministic grounded offline mode.
