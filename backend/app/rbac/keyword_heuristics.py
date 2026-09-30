"""Lightweight keyword heuristics used only to produce a *friendly* RBAC
refusal message before hitting retrieval at all (e.g. "As a nurse, you don't
have access to billing documents...").

This is a UX nicety, NOT the security boundary. The real enforcement happens
because `hybrid_rag_query` is only ever given the caller's
`get_accessible_collections(role)` list, so a metadata-filtered vector query
physically cannot return chunks outside it - even if a question sneaks past
these keyword checks (e.g. a prompt-injection attempt), no restricted chunk
is ever fetched or shown to the LLM.
"""
import re

COLLECTION_KEYWORDS: dict[str, list[str]] = {
    "billing": [
        "billing", "insurance", "claim", "copay", "co-pay", "reimbursement",
        "invoice", "cpt code", "premium", "deductible", "payer",
    ],
    "clinical": [
        "drug formulary", "diagnostic protocol", "treatment protocol",
        "dosage", "prescription guideline", "clinical protocol",
    ],
    "nursing": [
        "icu procedure", "infection control", "nursing procedure",
        "catheter care", "ward nursing",
    ],
    "equipment": [
        "calibration", "equipment manual", "maintenance schedule",
        "device maintenance", "ventilator manual",
    ],
}


def _contains_keyword(lowered_text: str, keyword: str) -> bool:
    """Word-boundary match so short keywords (e.g. "count", "sum") don't
    false-positive inside unrelated words ("discount", "summary")."""
    return re.search(rf"\b{re.escape(keyword)}\b", lowered_text) is not None


def find_restricted_collection_mention(question: str, allowed_collections: list[str]) -> str | None:
    """Return the name of a restricted collection the question appears to be
    asking about, or None if no obvious restricted-topic keyword is found."""
    lowered = question.lower()
    for collection, keywords in COLLECTION_KEYWORDS.items():
        if collection in allowed_collections:
            continue
        if any(_contains_keyword(lowered, keyword) for keyword in keywords):
            return collection
    return None
