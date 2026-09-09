# Groww Mutual Fund RAG Assistant

## Overview
This is a Retrieval-Augmented Generation (RAG) chatbot designed to answer factual inquiries about mutual fund schemes using an approved, verified source corpus. The assistant strictly adheres to a facts-only policy and does not provide investment advice, speculative predictions, or scheme recommendations.

---

## Live Demo
The application is deployed and live at:  
👉 **[https://ragchatbotmutualfunds.streamlit.app/](https://ragchatbotmutualfunds.streamlit.app/)**

---

## Key Features
- **RAG-Based Retrieval**: Retrieves accurate scheme disclosures and metrics from structured, pre-processed documents.
- **Facts-Only Responses**: Enforces strict boundaries to deliver objective answers without subjective advice or opinions.
- **Source & Citation Grounding**: Attributes factual responses to official Groww scheme disclosure pages with verified links.
- **Investment-Advice Refusal Guardrails**: Detects and politely refuses advisory, recommendation, or comparative queries, directing users to official investor education resources (such as AMFI).
- **PII Protection**: Identifies personal identifiers (PAN, folio numbers, bank accounts) and suppresses external links to protect privacy.
- **Retrieval Confidence Controls**: Rejects questions outside the designated corpus or below confidence thresholds to prevent hallucinations.
- **Scheduled Data Freshness**: Automated daily GitHub Actions workflow that re-fetches scheme disclosures, rebuilds vector indices, and runs smoke tests.

---

## Supported Mutual Fund Schemes
The assistant is strictly scoped to the following 5 schemes defined in `corpus/sources.json`:
- **HDFC Mid-Cap Opportunities Fund** (Direct Plan - Growth Option)
- **HDFC Flexi Cap Fund** (Direct Plan - Growth Option)
- **HDFC Focused 30 Fund** (Direct Plan - Growth Option)
- **HDFC ELSS Tax Saver Fund** (Direct Plan - Growth Option)
- **HDFC Top 100 Fund** (Direct Plan - Growth Option)

---

## How It Works
1. **User Query**: The user asks a question via the Streamlit chat interface.
2. **Intent & Safety Check**: The system screens for PII, investment-advice intent, or out-of-scope AMCs.
3. **Retrieval**: The retriever identifies the target scheme and topic, matching the query against atomic scheme chunks using TF-IDF vector similarity.
4. **Grounded Generation**: Groq LLM synthesizes a concise response (up to 3 sentences) using only retrieved source context.
5. **Post-Validation & Citation**: The answer is formatted, verified against length limits, and appended with the exact Groww source URL and data timestamp.

---

## Tech Stack
- **Language**: Python 3.11+
- **Web App**: Streamlit
- **LLM / Generation**: Groq Cloud API (`openai/gpt-oss-120b` with fallback to `openai/gpt-oss-20b`)
- **Indexing & Retrieval**: Scikit-Learn (TF-IDF Vectorizer & Cosine Similarity), NumPy
- **Ingestion & Parsing**: BeautifulSoup4, Requests
- **Data Validation**: Pydantic
- **CI/CD & Automation**: GitHub Actions

---

## Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/deeksha-v-hegde/RAG-Chatbot.git
cd RAG-Chatbot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory (or copy `.env.example`):
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_PRIMARY_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b
```
*(Note: A Groq API key enables LLM synthesis. If omitted, the system falls back to deterministic grounded synthesis).*

### 4. Start the Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Deployment
The application is deployed on **Streamlit Community Cloud** with continuous deployment from the `main` branch.  
Live Demo: **[https://ragchatbotmutualfunds.streamlit.app/](https://ragchatbotmutualfunds.streamlit.app/)**

---

## License
Distributed under the MIT License.
