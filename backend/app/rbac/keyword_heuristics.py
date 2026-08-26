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


# Generic "sounds like a numbers question" phrasing. On its own this is too
# broad - "how many leaves do I have" would match just as well as "how many
# claims were escalated" - so it must co-occur with a DOMAIN_KEYWORDS hit
# below before being treated as analytical.
ANALYTICAL_KEYWORDS = [
    "how many", "how much", "count", "total", "average", "avg", "sum",
    "percentage", "percent", "number of", "statistics", "trend",
    "compare", "breakdown",
]

# SQL RAG (Component 4) only ever queries the `claims` and `maintenance_tickets`
# tables in mediassist.db - these are the actual columns/values in those two
# tables (see app.db.sqlite.get_schema_summary()), so a question has to
# plausibly be about one of them to count as analytical.
DOMAIN_KEYWORDS = [
    "claim", "claims", "insurer", "insurance", "diagnosis", "department",
    "patient", "reimbursement", "billing", "escalated",
    "ticket", "tickets", "equipment", "maintenance", "campus", "fault",
    "calibration", "raised", "resolved",
]


def looks_analytical(question: str) -> bool:
    """Very simple keyword heuristic to decide whether a question likely
    needs SQL RAG (structured data) vs document RAG. Requires both a
    quantifier-style word AND a claims/maintenance-domain word, so generic
    "how many X" questions unrelated to those two tables (e.g. "how many
    leaves do I have") fall through to hybrid RAG instead. Replace with an
    LLM-based router if you want smarter classification - this is
    intentionally non-AI so the endpoint works before Components 1-4 land.
    """
    lowered = question.lower()
    has_quantifier = any(_contains_keyword(lowered, keyword) for keyword in ANALYTICAL_KEYWORDS)
    has_domain_word = any(_contains_keyword(lowered, keyword) for keyword in DOMAIN_KEYWORDS)
    return has_quantifier and has_domain_word
