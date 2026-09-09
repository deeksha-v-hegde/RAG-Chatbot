# Deployment Guide: Streamlit Community Cloud & Local

This guide explains how to run and deploy the **Compliance-Aware Mutual Fund FAQ Assistant** using Streamlit.

---

## 1. Local Deployment

### Prerequisites
- Python 3.10+ (Python 3.11 / 3.12 / 3.14 supported)
- Groq API Key (from [console.groq.com](https://console.groq.com))

### Steps

1. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Ensure your `.env` file contains your Groq API key:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   GROQ_PRIMARY_MODEL=openai/gpt-oss-120b
   GROQ_FALLBACK_MODEL=openai/gpt-oss-20b
   ```

3. **Start the Streamlit Application:**
   ```powershell
   streamlit run app.py
   ```

4. **Access the Web App:**
   Open your browser at [http://localhost:8501](http://localhost:8501).

---

## 2. Deploying to Streamlit Community Cloud (Free)

[Streamlit Community Cloud](https://streamlit.io/cloud) allows you to host this application for free directly from your GitHub repository.

### Step 1: Push Code to GitHub
Ensure all code and the `requirements.txt` file are committed and pushed to your GitHub repository:
```bash
git add .
git commit -m "Add Streamlit application and deployment configuration"
git push origin main
```

### Step 2: Connect to Streamlit Community Cloud
1. Sign in to [share.streamlit.io](https://share.streamlit.io) with your GitHub account.
2. Click **"New app"**.
3. Select your repository: `<your-username>/RAG-Chatbot` (or your repository name).
4. Set the **Branch**: `main` (or `master`).
5. Set the **Main file path**: `app.py`.

### Step 3: Configure Cloud Secrets
1. In the app creation dialog (or via **App Settings -> Secrets**), paste:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   GROQ_PRIMARY_MODEL = "openai/gpt-oss-120b"
   GROQ_FALLBACK_MODEL = "openai/gpt-oss-20b"
   ```
2. Click **Save**.

### Step 4: Deploy!
- Click **"Deploy!"**.
- Streamlit Cloud will automatically install dependencies from `requirements.txt` and launch your live application with a public URL (e.g., `https://your-rag-chatbot.streamlit.app`).

---

## 3. Key Compliance & Regulatory Features in Streamlit

| Feature | Enforcement Mechanism |
| :--- | :--- |
| **Facts-Only Enforcement** | Intent classifier intercepts ADVISORY, COMPARISON, and PREDICTION queries, redirecting to AMFI. |
| **Strict Zero-URL Defense** | If a query contains PII or requests info outside the 5 schemes, **0 URLs** are attached. |
| **Groww Scheme Citations** | Valid factual queries receive exactly 1 whitelisted Groww scheme URL. |
| **Max 3 Sentences** | Post-validator strictly trims responses to $\le 3$ sentences. |
| **Corpus Date Stamp** | Every factual output includes `Last updated from sources: <YYYY-MM-DD>`. |
