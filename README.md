# 📈 Groww Mutual Fund RAG Assistant

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ragchatbotmutualfunds.streamlit.app/)
[![Scheduled Data Freshness](https://github.com/deeksha-v-hegde/RAG-Chatbot/actions/workflows/data_freshness.yml/badge.svg)](https://github.com/deeksha-v-hegde/RAG-Chatbot/actions/workflows/data_freshness.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, compliance-aware Retrieval-Augmented Generation (RAG) assistant designed for mutual fund investor inquiries. Grounded exclusively on official scheme information documents and statutory disclosures for 5 designated HDFC mutual fund schemes from Groww.

---

## 🚀 Live Demo

**Deployed App URL**: [https://ragchatbotmutualfunds.streamlit.app/](https://ragchatbotmutualfunds.streamlit.app/)

---

## 🌟 Key Capabilities & Compliance Architecture

- **Strict Regulatory Guardrails**:
  - **Zero-URL PII Defense**: Automatically strips URLs and rejects sensitive personal data (PAN, Folio, Bank Account).
  - **No Investment Advice**: Rejects speculative inquiries, forward return guarantees, and comparative advice with AMFI investor links.
  - **Sentence Length & Metric Grounding**: Strict length limit ($\le 3$ sentences) with citation directly to the official Groww disclosure page.
- **Deterministic 5-Scheme Whitelist**:
  - `HDFC Mid-Cap Opportunities Fund` (Direct - Growth)
  - `HDFC Flexi Cap Fund` (Direct - Growth)
  - `HDFC Focused 30 Fund` (Direct - Growth)
  - `HDFC ELSS Tax Saver Fund` (Direct - Growth)
  - `HDFC Top 100 Fund` (Direct - Growth)
- **Automated Data Freshness (GitHub Actions)**:
  - Daily scheduled cron job at **10:00 AM IST (04:30 UTC)** to re-scrape official disclosures, rebuild vector indices, and push updates without manual intervention.

---

## 🛠️ Quickstart (Run Locally)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/deeksha-v-hegde/RAG-Chatbot.git
cd RAG-Chatbot
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file (or copy `.env.example`):
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_PRIMARY_MODEL=openai/gpt-oss-120b
GROQ_FALLBACK_MODEL=openai/gpt-oss-20b
```

### 3. Launch Application
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deployment (Streamlit Community Cloud)

1. Sign in to [share.streamlit.io](https://share.streamlit.io) with your GitHub account.
2. Click **"New app"** and select repository `deeksha-v-hegde/RAG-Chatbot`.
3. Set **Main file path** to `app.py`.
4. Under **Advanced settings -> Secrets**, add your Groq API credentials:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   GROQ_PRIMARY_MODEL = "openai/gpt-oss-120b"
   GROQ_FALLBACK_MODEL = "openai/gpt-oss-20b"
   ```
5. Click **Deploy!**
