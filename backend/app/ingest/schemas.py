# backend/app/ingest/schemas.py

from typing import List, Optional
from pydantic import BaseModel


class ChunkMetadata(BaseModel):
    """
    Metadata associated with a chunk.
    """
    url: str
    title: Optional[str] = None


class Chunk(BaseModel):
    """
    Represents a single chunk of text from a document.
    """
    chunk_index: int
    chunk_text: str
    metadata: ChunkMetadata


class Document(BaseModel):
    """
    Represents a full document, including raw markdown and chunks.
    """
    document_id: int
    url: str
    title: Optional[str] = None
    markdown_content: str
    chunks: List[Chunk]


# class Embedding(BaseModel):
#     """
#     Represents a vector embedding for a chunk.
#     """
#     chunk_index: int
#     embedding_vector: List[float]


class IngestionResult(BaseModel):
    """
    Return type for the ingestion pipeline.
    """
    status: str
    document_id: int
    chunks: int