"""
Phase 4: RAG Prompting & Output Synthesis
Module: synthesizer.py

Master End-to-End RAG Synthesizer:
1. Intercepts queries via Phase 3 ComplianceGuardrail (PII, Advisory, Jailbreaks).
2. Retrieves top-1 atomic passage via Phase 2 SchemeRetriever (Disambiguation, Whitelist).
3. Invokes Phase 4 GroqLLMClient (zero-temperature, llama-3.3-70b-versatile).
4. Validates and post-normalizes via Phase 4 OutputValidator (<= 3 sentences, No-URL rules).
"""

import sys
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

# Add search paths for all phases
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root / "phase1" / "phase1.1"))
sys.path.insert(0, str(project_root / "phase2"))
sys.path.insert(0, str(project_root / "phase3"))
sys.path.insert(0, str(current_dir))

from registry import SchemeRegistry
from retriever import SchemeRetriever, RetrievalResult
from guardrails import ComplianceGuardrail, GuardrailDecision
from groq_client import GroqLLMClient
from prompt_templates import PromptBuilder, SYSTEM_PROMPT
from post_validator import OutputValidator, ValidationResult

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Phase4_Synthesizer")


@dataclass
class SynthesizerResponse:
    query: str
    answer: str
    markdown_output: str
    is_refusal: bool = False
    is_disambiguation: bool = False
    is_unknown: bool = False
    source_url: str = ""
    citation_title: str = ""
    last_updated: str = ""
    model_used: str = ""
    sentence_count: int = 0
    url_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "markdown_output": self.markdown_output,
            "is_refusal": self.is_refusal,
            "is_disambiguation": self.is_disambiguation,
            "is_unknown": self.is_unknown,
            "source_url": self.source_url,
            "citation_title": self.citation_title,
            "last_updated": self.last_updated,
            "model_used": self.model_used,
            "sentence_count": self.sentence_count,
            "url_count": self.url_count,
            "metadata": self.metadata,
        }


class RAGSynthesizer:
    """Orchestrates end-to-end question answering from raw query to verified response."""

    def __init__(
        self,
        guardrail: Optional[ComplianceGuardrail] = None,
        retriever: Optional[SchemeRetriever] = None,
        llm_client: Optional[GroqLLMClient] = None,
    ):
        self.guardrail = guardrail or ComplianceGuardrail()
        self.retriever = retriever or SchemeRetriever()
        self.llm_client = llm_client or GroqLLMClient()

    def answer_query(self, query: str) -> SynthesizerResponse:
        """Processes query through guardrails -> retriever -> Groq LLM -> validator."""
        clean_query = query.strip()
        logger.info(f"Processing query: '{clean_query}'")

        # ------------------------------------------------------------------
        # Step 1: Upstream Guardrails (Phase 3)
        # ------------------------------------------------------------------
        decision: GuardrailDecision = self.guardrail.evaluate(clean_query)
        if decision.is_refusal:
            logger.info(f"Refusal triggered by Guardrail [{decision.intent.value}]: {decision.reason}")
            refusal = decision.refusal_response
            is_pii = "PII" in decision.reason

            # Run validator to enforce strict URL rules (0 URLs for PII)
            val_res = OutputValidator.validate(
                refusal.full_markdown,
                is_pii=is_pii,
                expected_url=refusal.citation_url if not is_pii else "",
            )

            return SynthesizerResponse(
                query=clean_query,
                answer=refusal.answer,
                markdown_output=val_res.cleaned_markdown,
                is_refusal=True,
                is_disambiguation=False,
                is_unknown=False,
                source_url=refusal.citation_url if not is_pii else "",
                citation_title=refusal.citation_title if not is_pii else "",
                last_updated=refusal.last_updated if not is_pii else "",
                model_used="GuardrailEngine",
                sentence_count=val_res.sentence_count,
                url_count=val_res.url_count,
                metadata={"reason": decision.reason, "intent": decision.intent.value},
            )

        # ------------------------------------------------------------------
        # Step 2: Entity-Aware Retrieval (Phase 2)
        # ------------------------------------------------------------------
        ret_result: RetrievalResult = self.retriever.retrieve(clean_query, top_k=1)

        # 2a. Out-of-Corpus Foreign AMC Scheme
        if ret_result.is_unsupported_scheme:
            logger.info(f"Out of corpus query detected: {ret_result.status_message}")
            val_res = OutputValidator.validate(ret_result.status_message, is_unknown=True)
            return SynthesizerResponse(
                query=clean_query,
                answer=ret_result.status_message,
                markdown_output=val_res.cleaned_markdown,
                is_refusal=True,
                is_disambiguation=False,
                is_unknown=True,
                source_url="",
                citation_title="",
                last_updated="",
                model_used="RetrieverBoundaryFilter",
                sentence_count=val_res.sentence_count,
                url_count=0,
                metadata={"reason": "UNSUPPORTED_SCHEME"},
            )

        # 2b. Missing Scheme Disambiguation
        if ret_result.is_disambiguation:
            logger.info(f"Disambiguation triggered: {ret_result.status_message}")
            val_res = OutputValidator.validate(ret_result.status_message, is_unknown=True)
            return SynthesizerResponse(
                query=clean_query,
                answer=ret_result.status_message,
                markdown_output=val_res.cleaned_markdown,
                is_refusal=False,
                is_disambiguation=True,
                is_unknown=False,
                source_url="",
                citation_title="",
                last_updated="",
                model_used="DisambiguationRouter",
                sentence_count=val_res.sentence_count,
                url_count=0,
                metadata={"reason": "AMBIGUOUS_SCHEME"},
            )

        top_chunk = ret_result.top_chunk
        if not top_chunk:
            # Unknown / No context found -> STRICT NO-URL RULE
            msg = "This specific information is not available in the official scheme disclosures for the 5 designated HDFC mutual fund schemes in our current corpus."
            val_res = OutputValidator.validate(msg, is_unknown=True)
            return SynthesizerResponse(
                query=clean_query,
                answer=msg,
                markdown_output=val_res.cleaned_markdown,
                is_refusal=False,
                is_disambiguation=False,
                is_unknown=True,
                source_url="",
                citation_title="",
                last_updated="",
                model_used="None",
                sentence_count=val_res.sentence_count,
                url_count=0,
                metadata={"reason": "NO_CONTEXT"},
            )

        # ------------------------------------------------------------------
        # Step 3: Groq LLM Synthesis (Phase 4)
        # ------------------------------------------------------------------
        user_prompt = PromptBuilder.build_rag_prompt(clean_query, top_chunk)
        raw_llm_response = self.llm_client.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.0,
            max_tokens=800,
            retrieved_chunk=top_chunk,
        )

        if not raw_llm_response or not raw_llm_response.strip():
            logger.warning("Groq response was empty; using structured grounded fallback.")
            raw_llm_response = self.llm_client._generate_offline_grounded(clean_query, top_chunk)

        # ------------------------------------------------------------------
        # Step 4: Output Post-Validation Layer (Phase 4.2)
        # ------------------------------------------------------------------
        is_unknown_response = (
            "information is not available" in raw_llm_response.lower()
            or "not available in the official scheme disclosures" in raw_llm_response.lower()
            or "unavailable in the current corpus" in raw_llm_response.lower()
            or "context does not contain" in raw_llm_response.lower()
        )

        val_res: ValidationResult = OutputValidator.validate(
            raw_text=raw_llm_response,
            expected_url=top_chunk.get("source_url") if not is_unknown_response else None,
            is_unknown=is_unknown_response,
            last_updated=top_chunk.get("last_updated", "2026-09-09"),
        )

        return SynthesizerResponse(
            query=clean_query,
            answer=val_res.cleaned_markdown.split("\n\nSource:")[0].strip(),
            markdown_output=val_res.cleaned_markdown,
            is_refusal=False,
            is_disambiguation=False,
            is_unknown=is_unknown_response,
            source_url=top_chunk.get("source_url") if not is_unknown_response else "",
            citation_title=top_chunk.get("citation_label") if not is_unknown_response else "",
            last_updated=top_chunk.get("last_updated", "2026-09-09") if not is_unknown_response else "",
            model_used=self.llm_client.model if self.llm_client.is_live_api_active else "GroqOfflineGroundedEngine",
            sentence_count=val_res.sentence_count,
            url_count=val_res.url_count,
            metadata={
                "chunk_id": top_chunk.get("chunk_id"),
                "retrieval_score": ret_result.top_score,
                "validation_errors": val_res.validation_errors,
            },
        )


if __name__ == "__main__":
    synthesizer = RAGSynthesizer()
    samples = [
        "What is the exit load for HDFC Mid Cap?",
        "Tell me the expense ratio of HDFC Flexicap",
        "What is the lock-in period for HDFC ELSS?",
        "Should I invest in HDFC Top 100?",
        "My PAN is ABCDE1234F check my units",
        "What is the exit load?",
        "What is the expense ratio of SBI Small Cap?",
    ]
    for s in samples:
        resp = synthesizer.answer_query(s)
        print(f"\n==================================================")
        print(f"Query: '{s}'")
        print(f"Model: {resp.model_used} | Refusal: {resp.is_refusal} | URLs: {resp.url_count}")
        print("Response:\n" + resp.markdown_output)
