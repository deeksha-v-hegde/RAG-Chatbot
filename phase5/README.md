# Phase 5: Minimal Web Interface & API Layer

> **Status:** 100% Complete  
> **Compliance Banner:** `Facts-only. No investment advice.`  
> **Framework:** FastAPI + Vanilla HTML5/CSS3/JavaScript (Groww Dark Theme)

---

## 1. Overview

Phase 5 implements the user interface and serving layer as specified in [`docs/architecture.md`](../docs/architecture.md#L308-L337). It connects the user to the underlying RAG pipeline through:
1. A lightweight **FastAPI backend service** exposing `/health`, `/api/schemes`, and `/api/chat`.
2. A clean, responsive **Vanilla HTML/CSS/JS frontend** with modern Groww aesthetics, prominent compliance disclaimers, 1-click sample query pills, and structured citation cards.

---

## 2. Directory Structure

```
phase5/
├── __init__.py           # Package marker
├── api.py                # FastAPI server handling chat requests and static routing
├── run_server.py         # Uvicorn server launcher (reads HOST & PORT from .env)
├── test_phase5.py        # Integration test suite (FastAPI TestClient)
├── README.md             # Documentation
└── static/
    ├── index.html        # Semantic HTML5 single-page application
    ├── style.css         # Modern Groww CSS design system (dark theme, glassmorphism)
    └── app.js            # Client-side asynchronous interaction & dynamic card rendering
```

---

## 3. API Endpoints

### `GET /health`
Returns system health, corpus size, and active Groq LLM model:
```json
{
  "status": "healthy",
  "service": "Mutual Fund FAQ Assistant",
  "designated_schemes_count": 5,
  "corpus_amc": "HDFC Mutual Fund",
  "live_groq_api_active": true,
  "active_model": "openai/gpt-oss-120b",
  "total_indexed_chunks": 30
}
```

### `GET /api/schemes`
Returns the 5 canonical HDFC mutual fund schemes and their official Groww URLs.

### `POST /api/chat`
Processes questions through Guardrails $\rightarrow$ Entity-Gated Retrieval $\rightarrow$ Groq LLM Synthesis $\rightarrow$ Output Post-Validation:
- **Request Body:**
  ```json
  { "query": "What is the exit load for HDFC Mid-Cap Opportunities Fund?" }
  ```
- **Response Format:**
  ```json
  {
    "query": "What is the exit load for HDFC Mid-Cap Opportunities Fund?",
    "answer": "The exit load for HDFC Mid-Cap Opportunities Fund is 1% if redeemed within 1 year.",
    "markdown_output": "...",
    "citation_title": "Groww - HDFC Mid-Cap Opportunities Fund Direct-Growth",
    "citation_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "last_updated": "2026-09-09",
    "is_refusal": false,
    "is_disambiguation": false,
    "is_unknown": false,
    "model_used": "openai/gpt-oss-120b",
    "sentence_count": 1,
    "url_count": 1
  }
  ```

---

## 4. How to Run

### Run Integration Tests
```bash
python phase5/test_phase5.py
```

### Start the Web Application
```bash
python phase5/run_server.py
```
Or with uvicorn directly:
```bash
uvicorn phase5.api:app --reload --port 8000
```
Open your browser at: **`http://127.0.0.1:8000`**
