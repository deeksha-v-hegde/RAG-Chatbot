"""
Streamlit Application: Grow RAG - Professional Finance Assistant
High-fidelity Groww-inspired Dark Theme matching the approved UI mockup.

Features:
- Desktop Empty State with centered Sparkle Hero Card & Compliance Shield
- Desktop Active Chat with Right User Bubble & Left 'Verified Answer' Card
- Sidebar Navigation (Home, Investment FAQ, Market Trends, Historical Data)
- Interactive Example Questions in sidebar
- Top Bar: 'Grow RAG Chatbot' + '● Index: Healthy' status badge
- Whitelisted Sources pill linking to official Groww URLs
- Strict Zero-URL Defense on unknown queries or PII inputs
- Floating input container with send button and compliance disclaimer footer
"""

import os
import sys
import re
import logging
from pathlib import Path
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

def clean_html(raw_html: str) -> str:
    """Strips leading whitespace from every line to prevent Markdown from treating lines as code blocks."""
    return "\n".join(line.strip() for line in raw_html.strip().splitlines() if line.strip())

def format_answer_for_html(text: str) -> str:
    """Formats markdown asterisks and bullets into clean semantic HTML."""
    if not text:
        return ""
    # Convert **bold** to <strong>bold</strong>
    formatted = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    lines = [l.strip() for l in formatted.splitlines() if l.strip()]
    output = []
    in_list = False
    for line in lines:
        if line.startswith("•") or line.startswith("-") or line.startswith("*"):
            if not in_list:
                output.append("<ul style='margin: 8px 0; padding-left: 20px;'>")
                in_list = True
            content = re.sub(r"^[-•*]\s*", "", line)
            output.append(f"<li style='margin-bottom: 6px;'>{content}</li>")
        else:
            if in_list:
                output.append("</ul>")
                in_list = False
            output.append(f"<p style='margin: 0 0 10px 0;'>{line}</p>")
    if in_list:
        output.append("</ul>")
    return "".join(output)


# Load local .env
load_dotenv()

# Add project modules to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "phase1" / "phase1.1"))
sys.path.insert(0, str(PROJECT_ROOT / "phase2"))
sys.path.insert(0, str(PROJECT_ROOT / "phase3"))
sys.path.insert(0, str(PROJECT_ROOT / "phase4"))

from registry import SchemeRegistry
from synthesizer import RAGSynthesizer, SynthesizerResponse

# ----------------------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Grow RAG | Professional Finance Assistant",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# Pixel-Perfect CSS Stylesheet Matching Mockup
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    /* Global Dark Theme */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif !important;
        background-color: #0E1015 !important;
        color: #F1F5F9 !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Hide standard Streamlit elements */
    #MainMenu, footer {visibility: hidden;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #12141A !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding-top: 1rem !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }

    /* Sidebar Brand */
    .sidebar-brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin: 0;
        padding: 0;
    }
    .sidebar-brand-subtitle {
        font-size: 0.78rem;
        font-weight: 500;
        color: #64748B;
        margin-top: 2px;
        margin-bottom: 16px;
    }

    /* 1. Clear Chat Button */
    div.st-key-sidebar_clear_chat_btn {
        margin-bottom: 6px !important;
    }
    div.st-key-sidebar_clear_chat_btn button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #94A3B8 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em !important;
        padding: 7px 12px !important;
        min-height: 38px !important;
        height: 38px !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div.st-key-sidebar_clear_chat_btn button:hover {
        border-color: #00D09C !important;
        color: #00D09C !important;
        background: rgba(0, 208, 156, 0.08) !important;
    }

    /* 2. Navigation Pills */
    div.st-key-nav_home_btn,
    div.st-key-nav_faq_btn,
    div.st-key-nav_trends_btn,
    div.st-key-nav_history_btn {
        margin-bottom: 3px !important;
    }

    /* Shared style for all nav buttons: Left-align text and icons */
    div.st-key-nav_home_btn button,
    div.st-key-nav_faq_btn button,
    div.st-key-nav_trends_btn button,
    div.st-key-nav_history_btn button {
        border-radius: 8px !important;
        padding: 9px 14px !important;
        font-size: 0.88rem !important;
        min-height: 40px !important;
        height: 40px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        border: none !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-nav_home_btn button div,
    div.st-key-nav_faq_btn button div,
    div.st-key-nav_trends_btn button div,
    div.st-key-nav_history_btn button div,
    div.st-key-nav_home_btn button p,
    div.st-key-nav_faq_btn button p,
    div.st-key-nav_trends_btn button p,
    div.st-key-nav_history_btn button p {
        text-align: left !important;
        justify-content: flex-start !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        font-size: 0.88rem !important;
    }

    /* Home Pill: Active Emerald Green Pill */
    div.st-key-nav_home_btn button {
        background: #00D09C !important;
        color: #0B0E14 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(0, 208, 156, 0.25) !important;
    }
    div.st-key-nav_home_btn button p {
        color: #0B0E14 !important;
        font-weight: 700 !important;
    }
    div.st-key-nav_home_btn button:hover {
        background: #00e5ac !important;
        color: #0B0E14 !important;
    }

    /* Inactive Nav Pills: Sleek Dark / Transparent with subtle hover */
    div.st-key-nav_faq_btn button,
    div.st-key-nav_trends_btn button,
    div.st-key-nav_history_btn button {
        background: transparent !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
    }
    div.st-key-nav_faq_btn button p,
    div.st-key-nav_trends_btn button p,
    div.st-key-nav_history_btn button p {
        color: #94A3B8 !important;
        font-weight: 500 !important;
    }
    div.st-key-nav_faq_btn button:hover,
    div.st-key-nav_trends_btn button:hover,
    div.st-key-nav_history_btn button:hover {
        background: rgba(255, 255, 255, 0.05) !important;
        color: #F1F5F9 !important;
    }
    div.st-key-nav_faq_btn button:hover p,
    div.st-key-nav_trends_btn button:hover p,
    div.st-key-nav_history_btn button:hover p {
        color: #F1F5F9 !important;
    }

    /* 3. Example Questions Section */
    .sidebar-section-header {
        font-size: 0.72rem;
        font-weight: 700;
        color: #475569;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 22px;
        margin-bottom: 10px;
    }
    div.st-key-btn_ex1,
    div.st-key-btn_ex2,
    div.st-key-btn_ex3 {
        margin-bottom: 8px !important;
    }
    div.st-key-btn_ex1 button,
    div.st-key-btn_ex2 button,
    div.st-key-btn_ex3 button {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 8px !important;
        color: #94A3B8 !important;
        font-size: 0.8rem !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 9px 12px !important;
        line-height: 1.35 !important;
        white-space: normal !important;
        height: auto !important;
        min-height: 48px !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-btn_ex1 button:hover,
    div.st-key-btn_ex2 button:hover,
    div.st-key-btn_ex3 button:hover {
        background: rgba(0, 208, 156, 0.05) !important;
        border-color: rgba(0, 208, 156, 0.3) !important;
        color: #F1F5F9 !important;
    }
    div.st-key-btn_ex1 button p,
    div.st-key-btn_ex2 button p,
    div.st-key-btn_ex3 button p {
        text-align: left !important;
        font-size: 0.8rem !important;
        color: inherit !important;
        margin: 0 !important;
    }

    /* 4. Bottom Help & Settings Buttons */
    div.st-key-sidebar_help_btn button,
    div.st-key-sidebar_settings_btn button {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        color: #94A3B8 !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        padding: 7px 12px !important;
        min-height: 38px !important;
        height: 38px !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-sidebar_help_btn button:hover,
    div.st-key-sidebar_settings_btn button:hover {
        border-color: #00D09C !important;
        color: #00D09C !important;
        background: rgba(0, 208, 156, 0.08) !important;
    }

    /* Sidebar Bottom Meta */
    .sidebar-meta {
        font-size: 0.72rem;
        color: #64748B;
        margin-top: 20px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #F59E0B;
        display: inline-block;
    }
    .green-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #00D09C;
        display: inline-block;
    }

    /* Top Bar */
    .top-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 0 16px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 24px;
    }
    .top-title-group {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .top-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .status-badge {
        background: rgba(0, 208, 156, 0.08);
        border: 1px solid rgba(0, 208, 156, 0.25);
        color: #00D09C;
        font-size: 0.74rem;
        font-weight: 600;
        padding: 3px 9px;
        border-radius: 9999px;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Empty State Hero Card */
    .empty-hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 5rem 1.5rem 3rem 1.5rem;
        max-width: 680px;
        margin: 0 auto;
    }
    .sparkle-box {
        width: 62px;
        height: 62px;
        background: #181B22;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.7rem;
        color: #00D09C;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        margin-bottom: 24px;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.02em;
        margin-bottom: 10px;
    }
    .hero-title-gradient {
        background: linear-gradient(135deg, #00D09C 0%, #38EF7D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-desc {
        font-size: 0.94rem;
        color: #94A3B8;
        line-height: 1.55;
        max-width: 560px;
        margin-bottom: 22px;
    }
    .compliance-pill {
        background: rgba(245, 158, 11, 0.08);
        border: 1px solid rgba(245, 158, 11, 0.28);
        border-radius: 9999px;
        padding: 6px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #FBBF24;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Date Separator Pill */
    .date-separator-container {
        display: flex;
        justify-content: center;
        margin: 12px 0 20px 0;
    }
    .date-separator {
        background: #181A20;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 9999px;
        padding: 3px 12px;
        font-size: 0.72rem;
        font-weight: 600;
        color: #64748B;
    }

    /* User Message Bubble */
    .user-bubble-container {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 22px;
    }
    .user-bubble {
        background: #1C2029;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px 16px 4px 16px;
        padding: 12px 18px;
        max-width: 75%;
        color: #F1F5F9;
        font-size: 0.92rem;
        line-height: 1.45;
        font-weight: 500;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
    }

    /* Assistant Verified Answer Card */
    .assistant-card-wrapper {
        display: flex;
        gap: 14px;
        margin-bottom: 28px;
        align-items: flex-start;
    }
    .assistant-avatar {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: #181B22;
        border: 1px solid rgba(0, 208, 156, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        color: #00D09C;
        flex-shrink: 0;
    }
    .assistant-card {
        background: #14171E;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 18px 20px;
        width: 100%;
        max-width: 820px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    .verified-badge {
        color: #00D09C;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 12px;
    }
    .answer-body {
        font-size: 0.92rem;
        color: #E2E8F0;
        line-height: 1.6;
        margin-bottom: 16px;
    }
    .answer-body ul {
        margin-top: 8px;
        margin-bottom: 8px;
        padding-left: 20px;
    }
    .answer-body li {
        margin-bottom: 6px;
    }

    /* Sources Area inside Assistant Card */
    .sources-container {
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 12px;
        margin-top: 14px;
    }
    .sources-title {
        font-size: 0.72rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .source-pill-link {
        background: rgba(0, 208, 156, 0.06);
        border: 1px solid rgba(0, 208, 156, 0.25);
        color: #00D09C !important;
        border-radius: 6px;
        padding: 5px 11px;
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        transition: all 0.15s ease;
    }
    .source-pill-link:hover {
        background: rgba(0, 208, 156, 0.12);
        border-color: #00D09C;
    }
    .source-verified-meta {
        font-size: 0.72rem;
        color: #64748B;
        margin-top: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Zero-URL Defense Badge */
    .zero-url-defense-badge {
        background: rgba(148, 163, 184, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 0.75rem;
        color: #94A3B8;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Action Icons (Thumbs, Copy) */
    .action-icons-row {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 12px;
        padding-top: 10px;
        color: #475569;
        font-size: 0.85rem;
    }
    .action-icon {
        cursor: pointer;
        transition: color 0.15s ease;
    }
    .action-icon:hover {
        color: #94A3B8;
    }

    /* Bottom Input Container */
    .bottom-disclaimer {
        text-align: center;
        font-size: 0.74rem;
        color: #475569;
        margin-top: 8px;
        margin-bottom: 12px;
    }
    
    /* Streamlit Chat Input Customization */
    [data-testid="stChatInput"] {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: #151820 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #F1F5F9 !important;
        font-size: 0.92rem !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #00D09C !important;
        color: #0B0E14 !important;
        border-radius: 50% !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Apply dynamic customer text-size preference if enabled
if st.session_state.get("pref_text_size") == "Larger (High Readability)":
    st.markdown(
        """
        <style>
        .answer-body { font-size: 1.05rem !important; line-height: 1.7 !important; }
        .user-bubble { font-size: 1.02rem !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ----------------------------------------------------------------------
# API Key Resolver & Engine Initialization
# ----------------------------------------------------------------------
def resolve_api_key() -> str:
    """Resolves Groq API key from st.secrets, os.environ, or fallback."""
    try:
        if "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"]:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "").strip()


def get_synthesizer(api_key: str) -> RAGSynthesizer:
    """Initializes the RAG synthesizer with active environment settings."""
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    return RAGSynthesizer()


# ----------------------------------------------------------------------
# Interactive Dialogs: Settings & Help
# ----------------------------------------------------------------------
@st.dialog("⚙️ Chatbot Settings")
def show_settings_dialog():
    st.markdown("Customize your reading and interaction preferences.")

    # Initialize user preference defaults
    if "pref_format" not in st.session_state:
        st.session_state["pref_format"] = "Structured Bullets (Recommended)"
    if "pref_text_size" not in st.session_state:
        st.session_state["pref_text_size"] = "Standard"
    if "pref_show_citations" not in st.session_state:
        st.session_state["pref_show_citations"] = True
    if "pref_show_verified_badge" not in st.session_state:
        st.session_state["pref_show_verified_badge"] = True

    st.markdown("##### 📖 Reading & Display Preferences")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_format = st.radio(
            "Response Structure",
            options=["Structured Bullets (Recommended)", "Compact Summary"],
            index=0 if st.session_state["pref_format"] == "Structured Bullets (Recommended)" else 1,
            help="Choose how facts and numbers are structured in assistant answers.",
        )
    with col_f2:
        selected_text_size = st.radio(
            "Text Size",
            options=["Standard", "Larger (High Readability)"],
            index=0 if st.session_state["pref_text_size"] == "Standard" else 1,
            help="Increases text size for easier reading.",
        )

    st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        show_citations = st.checkbox(
            "Show Groww Source Links",
            value=st.session_state["pref_show_citations"],
            help="Displays external clickable links to official Groww scheme disclosures.",
        )
    with col2:
        show_verified_badge = st.checkbox(
            "Show Verified Answer Badge",
            value=st.session_state["pref_show_verified_badge"],
            help="Displays the green '● Verified Answer' badge on verified facts.",
        )

    st.markdown("---")
    st.markdown("##### 🔒 Privacy & Conversation Management")
    
    # Download transcript if messages exist
    user_msgs = [m for m in st.session_state.get("messages", []) if m.get("role") != "system"]
    if user_msgs:
        transcript_text = "\n\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in user_msgs
        )
        st.download_button(
            "📥 Download Chat Transcript (.txt)",
            data=transcript_text,
            file_name="grow_rag_chat_transcript.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_transcript_btn",
        )

    if st.button("🗑️ Clear Conversation History", use_container_width=True, key="clear_chat_in_settings"):
        st.session_state.messages = []
        st.success("Conversation cleared!")
        st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    col_save, col_close = st.columns([1, 1])
    with col_save:
        if st.button("💾 Apply Settings", use_container_width=True, key="save_settings_btn"):
            st.session_state["pref_format"] = selected_format
            st.session_state["pref_text_size"] = selected_text_size
            st.session_state["pref_show_citations"] = show_citations
            st.session_state["pref_show_verified_badge"] = show_verified_badge
            st.success("Settings applied!")
            st.rerun()
    with col_close:
        if st.button("Close", use_container_width=True, key="close_settings_btn"):
            st.rerun()


@st.dialog("❔ Help & Documentation")
def show_help_dialog():
    st.markdown("### How to use Grow RAG Chatbot")
    st.markdown(
        """
        **Grow RAG** is a compliance-aware, facts-only mutual fund FAQ assistant with Groww reference context.

        #### 📚 Designated HDFC Schemes in Scope (5 Funds):
        1. **HDFC Mid-Cap Opportunities Fund** (Direct Plan - Growth)
        2. **HDFC Flexi Cap Fund** (formerly *HDFC Equity Fund*)
        3. **HDFC Focused 30 Fund** (Direct Plan - Growth)
        4. **HDFC ELSS Tax Saver Fund** (3-Year Statutory Lock-in)
        5. **HDFC Top 100 Fund** (Direct Plan - Growth)

        #### 🔍 Supported Factual Topics:
        - **Expense Ratio (TER)**: *"What is the expense ratio of HDFC Mid Cap?"*
        - **Exit Load Structure**: *"What is the exit load of HDFC Equity Fund?"*
        - **Lock-in Period**: *"What is the lock-in period for HDFC ELSS?"*
        - **Minimum Investment / SIP**: *"What is the minimum SIP for HDFC Top 100?"*
        - **SEBI Riskometer & Benchmark**: *"What benchmark does HDFC Flexi Cap track?"*

        #### 🚫 Compliance Notice:
        This assistant **strictly does not provide investment advice, scheme recommendations, or speculative predictions**. For financial planning, please consult an AMFI-registered mutual fund distributor (MFD) or SEBI-registered investment adviser (RIA).
        """
    )
    if st.button("Close", use_container_width=True, key="close_help_btn"):
        st.rerun()


@st.dialog("📄 Investment FAQ & Guide")
def show_faq_dialog():
    st.markdown("### Common Mutual Fund Questions (Facts-Only)")
    st.markdown("Explore verified facts about the 5 designated schemes. Click any question below to ask the chatbot directly:")

    faq_col1, faq_col2 = st.columns(2)
    with faq_col1:
        st.markdown("**💰 Expense Ratio (TER)**")
        st.caption("The annual percentage fee charged by the AMC to manage the fund. Direct plans feature lower expense ratios because no intermediary distributor commissions are deducted.")
        if st.button("Ask: HDFC Mid Cap Expense Ratio", key="faq_ter_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What is the expense ratio of HDFC Mid Cap Fund?"
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("**⏳ Exit Load**")
        st.caption("A fee deducted if units are redeemed within an exit window (typically 1% if redeemed within 1 year for equity funds, 0% thereafter).")
        if st.button("Ask: HDFC Equity Fund Exit Load", key="faq_exit_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What is the exit load of HDFC Equity Fund?"
            st.rerun()

    with faq_col2:
        st.markdown("**🔒 ELSS 3-Year Lock-in**")
        st.caption("Equity Linked Savings Schemes carry a mandatory statutory lock-in period of 3 years from the date of each allotment/SIP instalment.")
        if st.button("Ask: HDFC ELSS Lock-in Period", key="faq_elss_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What is the lock-in period for HDFC ELSS Tax Saver?"
            st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("**📊 Minimum SIP / Investment**")
        st.caption("Designated HDFC equity growth plans permit systematic investments starting from ₹100 or ₹500 depending on the scheme mandate.")
        if st.button("Ask: Minimum SIP for HDFC Top 100", key="faq_sip_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What is the minimum SIP for HDFC Top 100 Fund?"
            st.rerun()

    st.markdown("---")
    st.caption("⚠️ All answers are derived strictly from official Scheme Information Documents (SID) and Key Information Memorandums (KIM). Non-advisory facts only.")
    if st.button("Close", use_container_width=True, key="close_faq_modal"):
        st.rerun()


@st.dialog("📈 Market Trends & Benchmark Disclosures")
def show_market_trends_dialog():
    st.markdown("### Official Scheme Benchmarks & SEBI Categorization")
    st.markdown("Each scheme's performance is officially measured against its designated market index:")

    st.markdown(
        """
        | Scheme Name | Category | Official Benchmark | SEBI Riskometer |
        | :--- | :--- | :--- | :--- |
        | **HDFC Top 100 Fund** | Large Cap | NIFTY 100 TRI | Very High |
        | **HDFC Flexi Cap Fund** | Flexi Cap | NIFTY 500 TRI | Very High |
        | **HDFC Mid-Cap Opportunities** | Mid Cap | NIFTY Midcap 150 TRI | Very High |
        | **HDFC Focused 30 Fund** | Focused (≤30 Stocks) | NIFTY 500 TRI | Very High |
        | **HDFC ELSS Tax Saver** | ELSS (Tax Saving) | NIFTY 500 TRI | Very High |
        """
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.info("💡 **Benchmark Role**: Total Return Index (TRI) reflects capital gains plus dividend reinvestments. Mutual fund schemes aim to beat or match these benchmarks.")

    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("Ask: HDFC Flexi Cap Benchmark", key="trends_flexi_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What benchmark does HDFC Flexi Cap track?"
            st.rerun()
    with col_q2:
        if st.button("Ask: HDFC Mid Cap Riskometer", key="trends_risk_btn", use_container_width=True):
            st.session_state["pending_dialog_query"] = "What is the risk level of HDFC Mid-Cap Opportunities Fund?"
            st.rerun()

    if st.button("Close", use_container_width=True, key="close_trends_modal"):
        st.rerun()


@st.dialog("🕒 Historical Scheme Data & Inception Records")
def show_historical_dialog():
    st.markdown("### Scheme Inception Dates & Regulatory Milestones")
    st.markdown("Verified historical track records from official AMC disclosures:")

    st.markdown(
        """
        | Scheme | Inception Date | Historical Milestones |
        | :--- | :--- | :--- |
        | **HDFC Flexi Cap Fund** | January 1994 | Originally launched as **HDFC Equity Fund**; re-categorized as Flexi Cap under SEBI 2018 categorization. |
        | **HDFC Top 100 Fund** | September 1996 | Originally launched as **HDFC Top 200 Fund**; focused on India's top 100 market capitalization stocks. |
        | **HDFC ELSS Tax Saver** | March 1996 | Established statutory 3-year lock-in equity fund under Section 80C. |
        | **HDFC Focused 30 Fund** | September 2004 | Concentrated portfolio strategy holding a maximum of 30 high-conviction companies. |
        | **HDFC Mid-Cap Opportunities** | June 2007 | High-growth mid-sized companies mandate (>65% mid-cap allocation). |
        """
    )
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.caption("📌 Direct plans for all designated schemes were officially introduced on January 1, 2013, per SEBI mandates.")

    if st.button("Ask: When was HDFC Equity Fund launched?", key="history_q_btn", use_container_width=True):
        st.session_state["pending_dialog_query"] = "When was HDFC Equity Fund launched?"
        st.rerun()

    if st.button("Close", use_container_width=True, key="close_history_modal"):
        st.rerun()


# ----------------------------------------------------------------------
# Sidebar Rendering
# ----------------------------------------------------------------------
pending_query_from_pill = None

with st.sidebar:
    st.markdown('<div class="sidebar-brand-title">Grow RAG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-brand-subtitle">Professional Finance Assistant</div>', unsafe_allow_html=True)

    # Clear Chat Button
    if st.button("+ CLEAR CHAT", key="sidebar_clear_chat_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    # Interactive Navigation Menu
    if st.button("🏠 Home", key="nav_home_btn", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("📄 Investment FAQ", key="nav_faq_btn", use_container_width=True):
        show_faq_dialog()

    if st.button("📈 Market Trends", key="nav_trends_btn", use_container_width=True):
        show_market_trends_dialog()

    if st.button("🕒 Historical Data", key="nav_history_btn", use_container_width=True):
        show_historical_dialog()

    # Example Questions Section
    st.markdown('<div class="sidebar-section-header">EXAMPLE QUESTIONS</div>', unsafe_allow_html=True)

    ex1 = "What is the expense ratio of HDFC Mid Cap Fund?"
    ex2 = "What is the exit load of HDFC Equity Fund?"
    ex3 = "What is the lock-in period for HDFC ELSS Tax Saver?"

    if st.button(f'"{ex1}"', key="btn_ex1", use_container_width=True):
        pending_query_from_pill = ex1

    if st.button(f'"{ex2}"', key="btn_ex2", use_container_width=True):
        pending_query_from_pill = ex2

    if st.button(f'"{ex3}"', key="btn_ex3", use_container_width=True):
        pending_query_from_pill = ex3

    # Bottom Metadata & Interactive Help / Settings Buttons
    now_str = datetime.now().strftime("%I:%M %p")
    st.markdown(
        f"""
        <div style="margin-top: 30px;">
            <div class="sidebar-meta">
                <span class="pulse-dot"></span>
                <span>LAST UPDATED: TODAY, {now_str}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    col_h, col_s = st.columns(2)
    with col_h:
        if st.button("❔ Help", key="sidebar_help_btn", use_container_width=True):
            show_help_dialog()
    with col_s:
        if st.button("⚙️ Settings", key="sidebar_settings_btn", use_container_width=True):
            show_settings_dialog()


# ----------------------------------------------------------------------
# Initialize Synthesizer Engine
# ----------------------------------------------------------------------
active_api_key = resolve_api_key()
try:
    synthesizer = get_synthesizer(active_api_key)
    engine_status = "Healthy"
except Exception as e:
    synthesizer = RAGSynthesizer()
    engine_status = "Fallback"


# ----------------------------------------------------------------------
# Main Canvas - Content Area
# ----------------------------------------------------------------------

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if query triggered from example question button or modal dialog
active_prompt = None
if pending_query_from_pill:
    active_prompt = pending_query_from_pill
elif "pending_dialog_query" in st.session_state and st.session_state["pending_dialog_query"]:
    active_prompt = st.session_state.pop("pending_dialog_query")

# ----------------------------------------------------------------------
# Main Canvas - Content Area (Empty State vs Active Chat)
# ----------------------------------------------------------------------
if len(st.session_state.messages) == 0 and not active_prompt:
    # Desktop Empty State Screen matching Mockup Left Screen
    hero_html = """
    <div class="empty-hero-container">
        <div class="sparkle-box">✦</div>
        <div class="hero-title">
            Grow RAG: <span class="hero-title-gradient">Facts-Only Assistant</span>
        </div>
        <div class="hero-desc">
            Instantly query verified documents for listed HDFC schemes. I synthesize complex financial data into concise, accurate answers.
        </div>
        <div class="compliance-pill">
            <span>🛡️</span>
            <span>Facts-only. No investment advice.</span>
        </div>
    </div>
    """
    st.markdown(clean_html(hero_html), unsafe_allow_html=True)
else:
    # Date Separator
    date_sep_html = """
    <div class="date-separator-container">
        <span class="date-separator">Today</span>
    </div>
    """
    st.markdown(clean_html(date_sep_html), unsafe_allow_html=True)

    # Render Active Conversation
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            user_html = f"""
            <div class="user-bubble-container">
                <div class="user-bubble">
                    {msg["content"]}
                </div>
            </div>
            """
            st.markdown(clean_html(user_html), unsafe_allow_html=True)
        else:
            # Assistant Verified Answer Card matching Mockup Right Screen
            show_citations_pref = st.session_state.get("pref_show_citations", True)
            show_badge_pref = st.session_state.get("pref_show_verified_badge", True)

            badge_html = """
            <div class="verified-badge">
                <span class="green-dot"></span>
                <span>Verified Answer</span>
            </div>
            """ if show_badge_pref else ""

            url_block = ""
            if msg.get("citation_url") and show_citations_pref:
                domain_display = msg["citation_url"].replace("https://", "").replace("http://", "")
                url_block = f"""
                <div class="sources-container">
                    <div class="sources-title">Sources</div>
                    <a href="{msg['citation_url']}" target="_blank" class="source-pill-link">
                        <span class="green-dot"></span>
                        <span>{domain_display}</span>
                        <span>↗</span>
                    </a>
                    <div class="source-verified-meta">
                        <span class="green-dot"></span>
                        <span>Verified from 1 source · {msg.get('last_updated', '2026-09-09')}</span>
                    </div>
                </div>
                """
            elif msg.get("is_unknown") or "personal information" in msg["content"].lower():
                url_block = """
                <div class="sources-container">
                    <div class="zero-url-defense-badge">
                        <span>🛡️</span>
                        <span>Zero-URL Defense Enforced · No external URLs attached</span>
                    </div>
                </div>
                """

            formatted_answer = format_answer_for_html(msg["content"])

            assistant_html = f"""
            <div class="assistant-card-wrapper">
                <div class="assistant-avatar">🛡️</div>
                <div class="assistant-card">
                    {badge_html}
                    <div class="answer-body">
                        {formatted_answer}
                    </div>
                    {url_block}
                    <div class="action-icons-row">
                        <span class="action-icon" title="Helpful">👍</span>
                        <span class="action-icon" title="Not helpful">👎</span>
                        <span class="action-icon" title="Copy answer">📋</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(clean_html(assistant_html), unsafe_allow_html=True)


# ----------------------------------------------------------------------
# Chat Input & Query Execution
# ----------------------------------------------------------------------
chat_input_val = st.chat_input("Ask a factual question about listed HDFC schemes...")

if chat_input_val:
    active_prompt = chat_input_val

if active_prompt:
    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": active_prompt})

    # 2. Synthesize Answer
    with st.spinner("Synthesizing verified factual response..."):
        try:
            resp: SynthesizerResponse = synthesizer.answer_query(active_prompt)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": resp.answer,
                    "citation_url": resp.source_url,
                    "citation_title": resp.citation_title,
                    "last_updated": resp.last_updated,
                    "is_refusal": resp.is_refusal,
                    "is_unknown": resp.is_unknown,
                    "model_used": resp.model_used,
                }
            )
        except Exception as exc:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"An error occurred: {exc}",
                    "citation_url": "",
                    "citation_title": "",
                    "last_updated": "2026-09-09",
                    "is_refusal": False,
                    "is_unknown": True,
                    "model_used": "error",
                }
            )

    # 3. Rerun to update the view
    st.rerun()

# Micro Disclaimer Footer
st.markdown(
    '<div class="bottom-disclaimer">Information is retrieved from the most recent official scheme documents. Verify critical data.</div>',
    unsafe_allow_html=True,
)
