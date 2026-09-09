"""
Phase 5: Minimal Web Interface & API Layer
Module: api.py

FastAPI serving layer providing:
- GET /health: Health check and corpus metadata
- GET /api/schemes: Catalog of the 5 designated HDFC mutual fund schemes
- POST /api/chat: Compliance-enforced RAG Q&A endpoint
- Mounts static files (HTML/CSS/JS) for the frontend web interface
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add paths to sys.path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))
sys.path.insert(0, str(project_root / "phase2"))
sys.path.insert(0, str(project_root / "phase3"))
sys.path.insert(0, str(project_root / "phase4"))

from registry import SchemeRegistry, WHITELISTED_URLS
from synthesizer import RAGSynthesizer, SynthesizerResponse

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase5_API")

# Initialize FastAPI application
app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="Compliance-Aware Facts-Only FAQ Assistant for 5 Designated HDFC Schemes on Groww",
    version="1.0.0",
)

# Enable CORS for browser interactions
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = current_dir / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Shared synthesizer instance
synthesizer = RAGSynthesizer()


# ----------------------------------------------------------------------
# Request & Response Schemas
# ----------------------------------------------------------------------

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="User question about mutual funds")


class ChatResponse(BaseModel):
    query: str
    answer: str
    markdown_output: str
    citation_title: str
    citation_url: str
    last_updated: str
    is_refusal: bool
    is_disambiguation: bool
    is_unknown: bool
    model_used: str
    sentence_count: int
    url_count: int


# ----------------------------------------------------------------------
# API Endpoints
# ----------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serves the Groww-themed single-page frontend."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>Mutual Fund FAQ Assistant is running. Static files are building...</h1>")


registry = SchemeRegistry()


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Returns system status, designated schemes count, and LLM readiness."""
    schemes = registry.get_all()
    return {
        "status": "healthy",
        "service": "Mutual Fund FAQ Assistant",
        "designated_schemes_count": len(schemes),
        "corpus_amc": "HDFC Mutual Fund",
        "live_groq_api_active": synthesizer.llm_client.is_live_api_active,
        "active_model": synthesizer.llm_client.model,
        "total_indexed_chunks": 30,
    }


@app.get("/api/schemes")
async def get_schemes() -> List[Dict[str, Any]]:
    """Returns the 5 designated canonical HDFC mutual fund schemes."""
    schemes = registry.get_all()
    return [
        {
            "scheme_id": s.scheme_id,
            "scheme_name": s.canonical_name,
            "category": s.category,
            "groww_url": s.source_url,
        }
        for s in schemes
    ]


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """Processes user queries through Guardrails -> Retrieval -> Synthesis -> Validation."""
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        resp: SynthesizerResponse = synthesizer.answer_query(query)
        return ChatResponse(
            query=resp.query,
            answer=resp.answer,
            markdown_output=resp.markdown_output,
            citation_title=resp.citation_title,
            citation_url=resp.source_url,
            last_updated=resp.last_updated,
            is_refusal=resp.is_refusal,
            is_disambiguation=resp.is_disambiguation,
            is_unknown=resp.is_unknown,
            model_used=resp.model_used,
            sentence_count=resp.sentence_count,
            url_count=resp.url_count,
        )
    except Exception as e:
        logger.error(f"Error processing query '{query}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal assistant error. Please try again.")
