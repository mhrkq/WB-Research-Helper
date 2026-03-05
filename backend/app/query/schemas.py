# backend/app/query/schemas.py

from pydantic import BaseModel, Field
from typing import List, Optional


class QueryRequest(BaseModel):
    """
    Request payload for the RAG query endpoint.
    """

    query: str = Field(..., description="User query text")
    top_k: int = Field(
        default=5,
        ge=1,       # greater than or equal to
        le=20,      # less than or equal to
        description="Number of final chunks returned after reranking"
    )

    document_id: Optional[int] = Field(
        default=None,
        description="Filter results by a specific document ID"
    )

    title_contains: Optional[str] = Field(
        default="",
        description="Filter results by document title substring"
    )


class QueryResult(BaseModel):
    """
    Represents a single retrieved chunk returned by the RAG pipeline.
    """

    document_id: int
    document_title: Optional[str] = None
    chunk_index: int
    chunk_text: str

    vector_similarity: float = Field(
        description="Cosine distance returned by pgvector search"
    )

    rerank_score: float = Field(
        description="CrossEncoder reranker score"
    )


class QueryResponse(BaseModel):
    """
    Final response returned to the client.
    """

    answer: str
    results: List[QueryResult]