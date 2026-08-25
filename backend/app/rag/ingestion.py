"""Component 1: Document ingestion with Docling & hierarchical chunking.

TODO - implement:
  1. Walk MEDIASSIST_DATA_PATH/<collection>/ for each of general, clinical,
     nursing, billing, equipment (see app.core.config.settings.mediassist_data_path).
  2. Parse each PDF/Markdown file with Docling, preserving structure
     (headings, tables, code blocks).
  3. Apply a hierarchical chunking strategy (section -> subsection -> paragraph/
     table) then a token-aware size limit as a second pass. Prefix each
     chunk's embedded text with its parent section heading.
  4. Attach the required metadata to every chunk:
       source_document, collection, access_roles, section_title, chunk_type
     (use app.rbac.access_matrix.COLLECTIONS[<collection>].roles for
     access_roles so ingestion and query-time RBAC stay in sync).
  5. Compute dense + sparse (BM25) vectors and upsert into Qdrant
     (settings.qdrant_url) so both are queryable together at retrieval time.

Run this as a standalone script (not on every API request) - see the tip in
the assignment about running ingestion once before a demo.
"""
from app.core.config import get_settings

settings = get_settings()


def run_ingestion() -> None:
    raise NotImplementedError(
        "Implement Docling parsing + hierarchical chunking + Qdrant upsert here. "
        f"Source documents expected under: {settings.mediassist_data_path}"
    )


if __name__ == "__main__":
    run_ingestion()
