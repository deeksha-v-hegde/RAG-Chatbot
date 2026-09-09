"""
Phase 4: RAG Prompting & Output Synthesis
Module: prompt_templates.py

Defines system prompts, RAG context injection templates, and grounding constraints
for the Groq LLM inference engine.
"""

from typing import Dict, Any, Optional

SYSTEM_PROMPT = """You are a facts-only mutual fund FAQ assistant with Groww reference context.
Rely strictly on the provided context. Do NOT extrapolate, speculate, or give investment advice.

Rules:
1. Maximum Length: Total answer body must be at most 3 sentences or bullet points.
2. Structure your factual answers clearly and readably in multiple lines:
   - Provide an introductory sentence identifying the scheme and metric (e.g. 'For HDFC Equity Fund (Flexi Cap), the exit load structure is as follows:').
   - Follow with 1 to 2 clear bullet points (•) highlighting key values, percentages, or conditions with numbers bolded (e.g. '• An exit load of **1.00%** is applicable if redeemed within 1 year.').
   - (Optional) A brief note sentence if present in context.
   - Do NOT collapse everything into a single paragraph or one sentence.
3. For known facts: Include exactly one verified source citation link in markdown format and the mandatory footer: 'Last updated from sources: <YYYY-MM-DD>'.
4. STRICT NO-URL RULE FOR UNKNOWN ANSWERS: If the provided context does NOT contain the answer, or if the detail is unknown/unverifiable, state clearly that the official information is unavailable in the current corpus and DO NOT attach any URL or citation link.
5. STRICT NO-URL RULE FOR PERSONAL INFORMATION: Never request, process, or link to anything involving personal account or identification information.
"""


class PromptBuilder:
    """Constructs structured user prompts with injected context chunks."""

    @staticmethod
    def build_rag_prompt(query: str, chunk: Optional[Dict[str, Any]] = None) -> str:
        """Constructs the prompt containing the user query and retrieved atomic passage."""
        if not chunk or not chunk.get("text"):
            return (
                f"User Question: {query}\n\n"
                "Retrieved Context: [No relevant context found in official scheme overview.]\n\n"
                "Instructions: Answer directly using the rules. If context is missing, follow Rule 4 (state unavailable, attach NO URL)."
            )

        context_text = chunk["text"]
        source_url = chunk.get("source_url", "")
        citation_label = chunk.get("citation_label", "Groww")
        last_updated = chunk.get("last_updated", "2026-09-09")

        extra_scheme_note = ""
        if chunk.get("scheme_id") == "hdfc_flexi_cap":
            extra_scheme_note = "\n[Note: HDFC Flexi Cap Fund was formerly known as HDFC Equity Fund.]"

        return (
            f"User Question: {query}\n\n"
            f"--- Official Retrieved Context ---\n"
            f"{context_text}{extra_scheme_note}\n"
            f"Canonical Source Link: [{citation_label}]({source_url})\n"
            f"Source Timestamp: {last_updated}\n"
            f"----------------------------------\n\n"
            f"Instructions:\n"
            f"- Answer the user question in a clear, multi-line structured format (introductory sentence + bullet points) in at most 3 sentences total.\n"
            f"- Bold critical metrics, percentages, or durations (e.g. **1.00%**, **3 years**).\n"
            f"- If the answer is present, format your response as:\n\n"
            f"For [Scheme Name], the [metric] is as follows:\n\n"
            f"• [Key fact with bold numbers/percentages]\n"
            f"• [Secondary condition or duration if applicable]\n\n"
            f"Source: [{citation_label}]({source_url})\n"
            f"Last updated from sources: {last_updated}\n\n"
            f"- If the context does NOT contain the answer to the specific question, state: "
            f"'This specific information is not available in the official scheme disclosures for the 5 designated HDFC mutual fund schemes.' "
            f"and DO NOT attach any URL or citation link."
        )


if __name__ == "__main__":
    sample_chunk = {
        "text": "[Scheme: HDFC Mid-Cap Opportunities Fund | Topic: Exit Load]\nThe exit load for HDFC Mid-Cap is 1% within 1 year.",
        "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "citation_label": "Groww - HDFC Mid-Cap Opportunities Fund Direct-Growth",
        "last_updated": "2026-09-09",
    }
    prompt = PromptBuilder.build_rag_prompt("What is the exit load for HDFC Mid Cap?", sample_chunk)
    print("--- Sample Prompt ---")
    print(prompt)
