"""Component 2: Hybrid retrieval (dense vector + BM25 sparse) against Qdrant.

TODO - implement:
  - Query Qdrant with BOTH a dense vector and a sparse (BM25) vector in a
    single query (Qdrant's query API / Fusion), not two separate calls
    merged in Python.
  - Apply a metadata filter on `access_roles` scoped to `allowed_collections`
    (and/or role) so restricted chunks are excluded by the vector store
    itself, before anything reaches the application.
  - Fetch a broad candidate set (e.g. top-10) - narrowing happens in
    app.rag.reranker, not here.

Each returned candidate should look like:
    {
        "text": str,
        "source_document": str,
        "collection": str,
        "section_title": str,
        "chunk_type": str,
        "score": float,
    }
"""


def hybrid_search(question: str, allowed_collections: list[str], top_k: int = 10) -> list[dict]:
    raise NotImplementedError(
        "Implement dense+BM25 hybrid search against Qdrant, filtered to "
        f"collections={allowed_collections!r}."
    )
