"""Ties Components 2+3 together: hybrid retrieval -> rerank -> LLM answer.

Until app.rag.retriever / app.rag.reranker / app.rag.llm are implemented,
this returns a clearly-labelled placeholder response so the rest of the
stack (FastAPI endpoints, frontend, RBAC) is fully testable end-to-end.
"""
import logging

from app.rag import reranker, retriever
from app.rag.llm import generate

logger = logging.getLogger(__name__)

PLACEHOLDER_NOTICE = (
    "This is a placeholder answer - Components 1-3 (Docling ingestion, hybrid "
    "dense+BM25 retrieval, and cross-encoder reranking) have not been implemented "
    "yet. Once wired up, this endpoint will retrieve, rerank, and cite real "
    "document passages from the collections you have access to."
)


def hybrid_rag_answer(question: str, allowed_collections: list[str]) -> dict:
    """Returns {"answer": str, "sources": list[dict]}.

    sources items look like: {source_document, section_title, collection}
    """
    try:
        candidates = retriever.hybrid_search(question, allowed_collections, top_k=10)
        top_chunks = reranker.rerank(question, candidates, top_n=3)
        context = "\n\n".join(f"[{c['section_title']}] {c['text']}" for c in top_chunks)
        answer = generate(
            system_prompt=(
                "You are MediBot, an assistant for MediAssist Health Network staff. "
                "Answer only using the provided context and cite sources."
            ),
            user_prompt=f"Context:\n{context}\n\nQuestion: {question}",
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
    except NotImplementedError as exc:
        logger.info("hybrid_rag_answer placeholder path: %s", exc)
        return {
            "answer": PLACEHOLDER_NOTICE,
            "sources": [
                {
                    "source_document": "(pending ingestion)",
                    "section_title": "(pending ingestion)",
                    "collection": collection,
                }
                for collection in allowed_collections
            ],
        }
