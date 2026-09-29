"""Component 2: Hybrid retrieval (dense vector + BM25 sparse) against Qdrant.

Both vectors are sent in a single `query_points` call with RRF fusion
happening inside Qdrant, not as two separate queries merged in Python - and
the `access_roles` filter is applied on every prefetch branch, so a
restricted chunk is never fetched in the first place, matching the
assignment's RBAC requirement.
"""
from functools import lru_cache

from fastembed import SparseTextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import (
    FieldCondition,
    Filter,
    Fusion,
    FusionQuery,
    MatchAny,
    Prefetch,
)
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings
from app.rag.vector_config import (
    DENSE_VECTOR_NAME,
    EMBEDDING_MODEL,
    QDRANT_COLLECTION_NAME,
    SPARSE_EMBEDDING_MODEL,
    SPARSE_VECTOR_NAME,
)

settings = get_settings()


# Lazily loaded and cached (not module-level) so merely importing this file -
# e.g. when pytest collects unrelated auth tests - doesn't pay the cost of
# loading both embedding models. Loaded once per process on first real query.
@lru_cache(maxsize=1)
def _get_dense_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_sparse_model() -> SparseTextEmbedding:
    return SparseTextEmbedding(model_name=SPARSE_EMBEDDING_MODEL)


@lru_cache(maxsize=1)
def _get_client() -> QdrantClient:
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)


def hybrid_search(question: str, role: str, top_k: int = 10) -> list[dict]:
    dense_vector = _get_dense_model().encode(question, normalize_embeddings=True).tolist()
    sparse_vector = next(_get_sparse_model().embed([question]))

    # The security boundary: only chunks whose access_roles contains the
    # caller's role are ever fetched, on both the dense and sparse branch.
    role_filter = Filter(must=[FieldCondition(key="access_roles", match=MatchAny(any=[role]))])

    result = _get_client().query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        prefetch=[
            Prefetch(query=dense_vector, using=DENSE_VECTOR_NAME, filter=role_filter, limit=top_k),
            Prefetch(
                query={
                    "indices": sparse_vector.indices.tolist(),
                    "values": sparse_vector.values.tolist(),
                },
                using=SPARSE_VECTOR_NAME,
                filter=role_filter,
                limit=top_k,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=top_k,
        with_payload=True,
    )

    return [
        {
            "text": point.payload["content"],
            "source_document": point.payload["source_document"],
            "collection": point.payload["collection"],
            "section_title": point.payload["section_title"],
            "chunk_type": point.payload["chunk_type"],
            "score": point.score,
        }
        for point in result.points
    ]
