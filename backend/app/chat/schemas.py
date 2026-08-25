from typing import Literal

from pydantic import BaseModel

RetrievalType = Literal["hybrid_rag", "sql_rag", "rbac_blocked"]


class ChatRequest(BaseModel):
    question: str


class Source(BaseModel):
    source_document: str
    section_title: str
    collection: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    retrieval_type: RetrievalType
    role: str
