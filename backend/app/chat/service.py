"""Orchestrates the /chat request flow described in the assignment flowchart:

  question + role -> analytical? -> SQL RAG (if permitted)
                   -> otherwise   -> hybrid retrieval (RBAC-filtered) -> rerank -> LLM answer

RBAC is enforced by construction: hybrid_rag_answer is only ever given the
caller's own get_accessible_collections(role) list, and SQL RAG is only
invoked after can_use_sql_rag(role) passes. Nothing outside that allowed set
is ever fetched, so a restricted document can't leak through the LLM.
"""
import logging

from app.chat.schemas import ChatResponse
from app.rag.orchestrator import hybrid_rag_answer
from app.rag.sql_rag import sql_rag_chain
from app.rbac.access_matrix import can_use_sql_rag, get_accessible_collections
from app.rbac.keyword_heuristics import find_restricted_collection_mention, looks_analytical

logger = logging.getLogger(__name__)

SQL_RAG_PLACEHOLDER_NOTICE = (
    "[SQL RAG not yet implemented] Component 4 (NL -> SQL -> execute -> NL answer) "
    "has not been wired up yet. Once implemented, this will query the claims and "
    "maintenance_tickets tables in mediassist.db."
)


def handle_chat(question: str, role: str) -> ChatResponse:
    allowed_collections = get_accessible_collections(role)

    if looks_analytical(question):
        if not can_use_sql_rag(role):
            return ChatResponse(
                answer=(
                    f"As a {role.replace('_', ' ')}, you don't have access to analytical "
                    "database queries. SQL-based analytics over claims and maintenance "
                    "data are available only to billing executives and administrators."
                ),
                sources=[],
                retrieval_type="rbac_blocked",
                role=role,
            )
        try:
            answer = sql_rag_chain(question)
        except NotImplementedError as exc:
            logger.info("sql_rag_chain placeholder path: %s", exc)
            answer = SQL_RAG_PLACEHOLDER_NOTICE
        return ChatResponse(answer=answer, sources=[], retrieval_type="sql_rag", role=role)

    restricted = find_restricted_collection_mention(question, allowed_collections)
    if restricted:
        return ChatResponse(
            answer=(
                f"As a {role.replace('_', ' ')}, you don't have access to {restricted} "
                f"documents. I can only answer questions from the "
                f"{', '.join(allowed_collections)} collections."
            ),
            sources=[],
            retrieval_type="rbac_blocked",
            role=role,
        )

    result = hybrid_rag_answer(question, allowed_collections)
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        retrieval_type="hybrid_rag",
        role=role,
    )
