"""Classifies each question as 'analytical' (needs SQL RAG, over the
claims/maintenance_tickets database) or 'document' (needs hybrid RAG, over
the ingested PDF/Markdown documents).

An LLM call rather than a keyword list, because natural language has too
many ways to ask for the same data (superlatives like "most"/"least",
open-ended requests like "tell me about X", abbreviations like "max") for a
fixed word list to cover reliably. Defaults to 'document' if the
classification call itself fails, since a failed hybrid RAG answer degrades
gracefully (a normal "not covered by the available documents" response)
while running SQL RAG against a misclassified question would not.

`reasoning_effort="low"` is required for the current model
(openai/gpt-oss-20b, a reasoning model): without it, the model spends its
entire token budget on internal reasoning before emitting the one-word
answer, which reads as an empty response. If LLM_MODEL is ever changed to a
non-reasoning model, this parameter causes the Groq API call to error - the
try/except below already handles that by falling back to 'document', so
classification degrades safely either way, just without the latency benefit.
"""
import logging

from app.rag.llm import generate

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "Classify the user question into exactly one category. Respond with only "
    "the single word 'analytical' or 'document' - no punctuation, no explanation.\n\n"
    "'analytical': the question asks for real data recorded in the claims table or the "
    "maintenance_tickets table (counts, totals, averages, maximums/minimums, status, dates, "
    "or a general summary of the actual claims/tickets records).\n\n"
    "'document': the question asks about a policy RULE, CAP, or LIMIT that applies generally "
    "(e.g. to a category of patient/equipment, not one real record), or about a procedure, "
    "policy, dosage, or instructions.\n\n"
    "Examples:\n"
    '"Tell me about the claims" -> analytical (summary of the real claims records)\n'
    '"What is the maximum amount billed till date" -> analytical (a real historical value)\n'
    '"What is the maximum bill amount for a general ward patient" -> document (a policy cap '
    "that applies to a patient category, not one real claim)\n"
    '"What is the correct hand hygiene technique" -> document (a procedure)\n'
    '"How many leaves do I have" -> document (not in the claims/maintenance_tickets data at all)\n'
)


def classify_question(question: str) -> str:
    """Returns 'analytical' or 'document'."""
    try:
        raw = generate(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=question,
            temperature=0.0,
            reasoning_effort="low",
        )
    except Exception:
        logger.exception("Question classification failed (LLM provider unavailable)")
        return "document"

    return "analytical" if "analytical" in raw.lower() else "document"
