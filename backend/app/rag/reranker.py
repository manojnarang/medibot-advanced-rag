"""Component 3: Cross-encoder reranking.

TODO - implement:
  - Score each (question, candidate.text) pair jointly with a cross-encoder
    (e.g. sentence-transformers CrossEncoder), not independently.
  - Narrow the broad candidate set from app.rag.retriever.hybrid_search
    (e.g. top-10) down to a small final set (e.g. top-3).
  - Log scores during development - it's common for a lower-ranked hybrid
    result to score highest after reranking.

Only the reranked top candidates should ever be passed to the LLM prompt.
"""


def rerank(question: str, candidates: list[dict], top_n: int = 3) -> list[dict]:
    raise NotImplementedError(
        "Implement cross-encoder reranking of retriever candidates down to "
        f"top_n={top_n}."
    )
