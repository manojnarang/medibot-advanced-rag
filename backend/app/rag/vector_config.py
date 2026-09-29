"""Shared constants for the Qdrant-backed vector store.

Used by both app.rag.ingestion (writes) and app.rag.retriever (reads) so
they can never drift out of sync, and kept in its own module so retriever.py
- loaded by the live FastAPI app - doesn't have to import ingestion.py's
Docling dependencies just to get these names.
"""

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SPARSE_EMBEDDING_MODEL = "Qdrant/bm25"

# One Qdrant collection holds every document's chunks; RBAC is enforced at
# query time with an access_roles filter (see app.rbac.access_matrix), not by
# splitting into separate per-collection Qdrant collections.
QDRANT_COLLECTION_NAME = "mediassist_chunks"
DENSE_VECTOR_NAME = "dense"
SPARSE_VECTOR_NAME = "sparse"
