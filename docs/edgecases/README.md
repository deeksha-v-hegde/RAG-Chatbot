# Phase-Wise Edge Cases & Failure Modes

This directory documents the comprehensive analysis of edge cases, potential failure modes, adversarial inputs, and their mitigation strategies across all **6 phases** of the Mutual Fund FAQ Assistant.

---

## Edge Case Matrix by Phase

| Phase | Focus Area | Primary Failure Modes & Risks | Detailed Documentation |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **Corpus & Ingestion** | SPA Dynamic Rendering, DOM/Class Drift, Anti-Scraping/Rate Limiting, Truncated HTML | [Phase 1 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase1_ingestion.md) |
| **Phase 2** | **Indexing & Retrieval** | Unspecified Scheme Queries, Tabular Chunk Splitting, Acronym Ambiguity, Out-of-Corpus Funds | [Phase 2 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase2_indexing_retrieval.md) |
| **Phase 3** | **Guardrails & Refusal** | Indirect Advisory Prompts, Cross-Fund Comparison, PII Injection (PAN/Folio), Jailbreaks | [Phase 3 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase3_guardrails_refusal.md) |
| **Phase 4** | **Synthesis & Formatting** | Sentence Overflow (>3), Link Hallucination, Multiple Citations, Missing Date Footer | [Phase 4 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase4_synthesis_formatting.md) |
| **Phase 5** | **UI & API Layer** | Spam/Payload Flooding, Double Submissions, Latency Spikes, Mobile Wrap Breakage | [Phase 5 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase5_ui_api.md) |
| **Phase 6** | **Evaluation & Auditing** | Over-Refusal of Factual Risk, Subtle Opinion Leakage, Scraped URL Drift | [Phase 6 Edge Cases](file:///c:/Users/Admin/Projects/RAG%20Chatbot/docs/edgecases/phase6_evaluation.md) |

---

## Guiding Principles for Edge Case Handling

1. **Compliance & Guardrails Over Generative Creativity:** If an edge-case query falls into a grey area between fact and opinion, the system must default to polite refusal.
2. **Zero-PII Tolerance:** Any query containing sensitive identifiers (PAN, Aadhaar, folio numbers, bank accounts, passwords) is intercepted and terminated before vector retrieval or LLM inference.
3. **Deterministic Output Guarantees:** Output constraints ($\le 3$ sentences, exactly 1 official citation link, mandatory date footer) are validated by algorithmic post-processors rather than relying solely on LLM compliance.
