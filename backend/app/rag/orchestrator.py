"""Ties Components 2+3 together: hybrid retrieval -> rerank -> LLM answer."""
import logging

from fastapi import HTTPException, status

from app.rag import reranker, retriever
from app.rag.llm import generate

logger = logging.getLogger(__name__)


def hybrid_rag_answer(question: str, role: str) -> dict:
    """Returns {"answer": str, "sources": list[dict]}.

    sources items look like: {source_document, section_title, collection}

    RBAC enforcement happens inside hybrid_search, filtering on the chunk's
    access_roles against `role`.
    """
    try:
        candidates = retriever.hybrid_search(question, role, top_k=10)
        top_chunks = reranker.rerank(question, candidates, top_n=3)
        context = "\n\n".join(f"[{c['section_title']}] {c['text']}" for c in top_chunks)
        answer = generate(
            system_prompt=(
                "You are MediBot, an assistant for MediAssist Health Network staff. "
                "Answer only using the provided context and cite sources."
            ),
            user_prompt=f"Context:\n{context}\n\nQuestion: {question}",
        )
    except Exception:
        # Qdrant or the LLM provider is unreachable/erroring - a real 503, not
        # a silent 200 with the failure hidden in the answer text, so it's
        # distinguishable from a genuine answer in logs and on the frontend.
        logger.exception("hybrid_rag_answer failed (Qdrant or LLM provider unavailable)")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Document search is temporarily unavailable. Please try again shortly.",
        )

    sources = [
        {
            "source_document": c["source_document"],
            "section_title": c["section_title"],
            "collection": c["collection"],
        }
        for c in top_chunks
    ]
    return {"answer": answer, "sources": sources}
