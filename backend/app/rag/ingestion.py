"""Component 1: Document ingestion with Docling & hierarchical chunking.

Lists every PDF/Markdown file under each collection folder
(MEDIASSIST_DATA_PATH/<collection>/), parses it with Docling preserving
structure (headings, tables, code blocks), splits into chunks first by
structure then by token size, attaches the required metadata to each chunk
(source_document, collection, access_roles, section_title, chunk_type -
access_roles read from app.rbac.access_matrix.COLLECTIONS so ingestion and
query-time RBAC stay in sync), then computes dense + sparse (BM25) vectors
and upserts into Qdrant.

Run this as a standalone script (not on every API request) - see the tip in
the assignment about running ingestion once before a demo.
"""


import sys
import uuid
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.types.doc import DoclingDocument
from fastembed import SparseTextEmbedding
from hierarchical.postprocessor import ResultPostprocessor
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
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
from app.rbac.access_matrix import COLLECTIONS

settings = get_settings()

data_path = settings.mediassist_data_path

# loading
def load_document(source: str) -> DoclingDocument :
    """
    Convert pdf/md file to a DoclingDocument using Docling

    """
    converter = DocumentConverter()
    result = converter.convert(source)
    if Path(source).suffix.lower() == ".pdf":
        # Needed for pdf (not md) bec ResultPostprocessor infers heading levels from PDF bounding-box/font
        # data (item.prov). Markdown headings already carry the right level
        # from the '#'/'##' syntax and have no prov data.
        ResultPostprocessor(result).process()
    return result.document
  

# DESIRED FORMAT:
# {
#    "headings":   ['AtliqAI HR Policies', 'Employment & Onboarding', 'Probation Period'],
#    "content":    "All new employees at AtliqAI are placed on a probation period of 6 months from...",
#    "chunk_text": "AtliqAI HR Policies > Employment & Onboarding > Probation Period\n\nAll new employees at AtliqAI are placed on a probation period of 6 months from..."
# }
def convert_chunk(chunker: HybridChunker, doc_chunk) -> dict:
    """
    Convert a Docling DocChunk into a plain dict.

    headings   → list preserved as-is
    content    → paragraph text
    chunk_text → breadcrumb + content, built by the chunker itself
                 (what gets embedded)
    """
    return {
        "headings":   doc_chunk.meta.headings or [],
        "content":    doc_chunk.text.strip(),
        "chunk_text": chunker.contextualize(chunk=doc_chunk),
    }


def get_collection_for_file(file_path: Path) -> str:
    """
    A file's collection is the name of the folder directly under
    MEDIASSIST_DATA_PATH that contains it, e.g.
    mediassist_data/clinical/formulary.pdf -> "clinical".
    """
    relative_path = file_path.relative_to(data_path)
    collection = relative_path.parts[0]
    if collection not in COLLECTIONS:
        raise ValueError(
            f"'{file_path}' is not inside a known collection folder "
            f"(expected one of {sorted(COLLECTIONS)}, found '{collection}')"
        )
    return collection


_CHUNK_TYPE_BY_DOCLING_LABEL = {
    "table": "table",
    "code": "code",
    "section_header": "heading",
    "title": "heading",
}

# When a chunk merges Docling items of different types (e.g. a heading
# merged with its paragraph), resolve to one type by this priority: losing
# a detected table/code block matters more than losing a heading label.
_CHUNK_TYPE_PRIORITY = ("table", "code", "heading")


def get_chunk_type(doc_chunk) -> str:
    """
    Map this chunk to one of the assignment's required chunk_type values
    (text, table, heading, code). Any Docling item label not in
    _CHUNK_TYPE_BY_DOCLING_LABEL (paragraph, list_item, caption, ...)
    counts as "text".
    """
    types_present = {
        _CHUNK_TYPE_BY_DOCLING_LABEL.get(item.label.value, "text")
        for item in doc_chunk.meta.doc_items
    }
    for chunk_type in _CHUNK_TYPE_PRIORITY:
        if chunk_type in types_present:
            return chunk_type
    return "text"


def prepare_chunk_metadata(file_path: Path, collection: str, doc_chunk) -> dict:
    """
    Build the metadata every chunk must carry for RBAC-aware retrieval:
      source_document, collection, access_roles, section_title, chunk_type

    access_roles is read from app.rbac.access_matrix.COLLECTIONS so ingestion
    and query-time RBAC checks always agree on who can see this collection.
    """
    headings = doc_chunk.meta.headings or []
    return {
        "source_document": file_path.name,
        "collection": collection,
        "access_roles": list(COLLECTIONS[collection].roles),
        "section_title": headings[-1] if headings else "",
        "chunk_type": get_chunk_type(doc_chunk),
    }



# ingesting
def run_ingestion() -> None:
   print("--------run_ingestion()----------")

   files = get_all_files()
   if not files:
      print(f"No PDF or Markdown files found under: {data_path}")
      return

   # max_tokens is left unset so HybridChunker reads it from the tokenizer's
   # own sentence_bert_config.json (256 for all-MiniLM-L6-v2) instead of a
   # hardcoded number that could drift from EMBEDDING_MODEL_NAME.
   tokenizer = HuggingFaceTokenizer.from_pretrained(EMBEDDING_MODEL)
   chunker = HybridChunker(tokenizer=tokenizer)
   all_chunks = []
   for file_path in files:
      print(f"\nProcessing: {file_path}")
      collection = get_collection_for_file(file_path)
      doc = load_document(str(file_path))
      print(f"Document loaded: {doc.name}")

      # Parse and chunk the document before moving to next file.
      doc_chunks = list(chunker.chunk(dl_doc=doc))
      print(f"Total chunks: {len(doc_chunks)}")

      chunks = [
         {
            **convert_chunk(chunker, chunk),
            **prepare_chunk_metadata(file_path, collection, chunk),
         }
         for chunk in doc_chunks
      ]
      for chunk in chunks[:3]:
         print("-" * 60)
         print(f"headings       : {chunk['headings']}")
         print(f"content        : {chunk['content'][:200]}...")
         print(f"chunk_text     : {chunk['chunk_text'][:200]}...")
         print(f"source_document: {chunk['source_document']}")
         print(f"collection     : {chunk['collection']}")
         print(f"access_roles   : {chunk['access_roles']}")
         print(f"section_title  : {chunk['section_title']}")
         print(f"chunk_type     : {chunk['chunk_type']}")

      all_chunks.extend(chunks)

   embeddings(all_chunks)



def get_all_files() -> list[Path]:
   directory_path = Path(data_path)
   valid_extensions = {'.md', '.pdf'}

   if not directory_path.is_dir():
      raise FileNotFoundError(
         f"MediAssist data directory does not exist: {directory_path.resolve()}"
      )

   return sorted(
      (
         file_path
         for file_path in directory_path.rglob('*')
         if file_path.is_file() and file_path.suffix.lower() in valid_extensions
      ),
      key=lambda path: str(path).lower(),
   )


def _ensure_collection(client: QdrantClient, dense_dim: int) -> None:
    """
    Create the collection with named dense + sparse vectors on first run, and
    a payload index on access_roles since every retrieval query filters on it
    (RBAC is enforced at the Qdrant query layer - app.rbac.access_matrix).
    """
    if client.collection_exists(QDRANT_COLLECTION_NAME):
        return

    client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config={
            DENSE_VECTOR_NAME: VectorParams(size=dense_dim, distance=Distance.COSINE),
        },
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(),
        },
    )
    client.create_payload_index(
        collection_name=QDRANT_COLLECTION_NAME,
        field_name="access_roles",
        field_schema=PayloadSchemaType.KEYWORD,
    )


# Dense embeddings — semantic understanding. Sparse (BM25) embeddings — exact
# keyword/terminology matches. Both are stored on the same point so a single
# Qdrant query can fuse them server-side (see Component 2's retrieval code).
def embeddings(all_chunks: list[dict]) -> None:
    if not all_chunks:
        print("No chunks to embed.")
        return

    texts = [chunk["chunk_text"] for chunk in all_chunks]

    print("Dense embedding model:", EMBEDDING_MODEL)
    dense_model = SentenceTransformer(EMBEDDING_MODEL)
    # normalize_embeddings=True must stay paired with Distance.COSINE in
    # _ensure_collection - cosine similarity assumes unit-length vectors.
    dense_vectors = dense_model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    print("Sparse embedding model:", SPARSE_EMBEDDING_MODEL)
    sparse_model = SparseTextEmbedding(model_name=SPARSE_EMBEDDING_MODEL)
    sparse_vectors = list(sparse_model.embed(texts))

    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    _ensure_collection(client, dense_dim=dense_model.get_embedding_dimension())

    # Qdrant point IDs must be an int or a UUID string, so chunks get a random
    # UUID rather than a stable id derived from their content. Re-running
    # ingestion on the same files therefore adds duplicate points instead of
    # replacing them - rerun against a fresh collection, or clear it first.
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector={
                DENSE_VECTOR_NAME: dense_vector.tolist(),
                SPARSE_VECTOR_NAME: SparseVector(
                    indices=sparse_vector.indices.tolist(),
                    values=sparse_vector.values.tolist(),
                ),
            },
            payload=chunk,
        )
        for chunk, dense_vector, sparse_vector in zip(all_chunks, dense_vectors, sparse_vectors)
    ]

    client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=points)

    print(f"Indexed {len(points)} chunks into Qdrant collection '{QDRANT_COLLECTION_NAME}'")
    print("Both dense (semantic) and sparse (BM25) vectors stored.")


if __name__ == "__main__":
    # Source PDFs can contain characters Windows' default console codepage
    # (cp1252) can't print; force UTF-8 so the debug output never crashes on
    # them regardless of which terminal this is run from.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    run_ingestion()
