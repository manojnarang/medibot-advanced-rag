"""Component 3: Cross-encoder reranking.

Hybrid search casts a wide net (top-10); a cross-encoder scores each
(question, candidate) pair jointly - reading them together, not
independently like the dense/sparse retrieval scores - and only the
narrowed top_n survive to reach the LLM prompt.
"""
import logging
from functools import lru_cache

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


# Lazily loaded and cached, not module-level, so importing this file doesn't
# pay the model-load cost for callers (e.g. pytest collecting unrelated
# tests) that never actually call rerank().
@lru_cache(maxsize=1)
def _get_reranker() -> CrossEncoder:
    return CrossEncoder(RERANKER_MODEL)


def rerank(question: str, candidates: list[dict], top_n: int = 3) -> list[dict]:
    if not candidates:
        return []

    pairs = [(question, candidate["text"]) for candidate in candidates]
    cross_encoder_scores = _get_reranker().predict(pairs)

    ranked = sorted(
        zip(candidates, cross_encoder_scores, range(1, len(candidates) + 1)),
        key=lambda item: item[1],
        reverse=True,
    )

    # Logged per the assignment's own tip: it's common for a lower-ranked
    # hybrid result to score highest after reranking - this makes that
    # reordering visible during development.
    for new_rank, (candidate, score, hybrid_rank) in enumerate(ranked, start=1):
        logger.info(
            "rerank: #%d (was hybrid #%d) score=%.4f section=%r",
            new_rank, hybrid_rank, score, candidate["section_title"],
        )

    return [{**candidate, "score": float(score)} for candidate, score, _ in ranked[:top_n]]
