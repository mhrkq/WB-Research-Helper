from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.database import get_db
from app.ingest.repositories import query_similar_chunks
from app.ingest.services.embedder import embed_chunks

router = APIRouter()


class QueryChatRequest(BaseModel):
    query: str
    top_k: int = 5


class QueryResult(BaseModel):
    document_id: int
    chunk_index: int
    chunk_text: str
    similarity: float


class QueryChatResponse(BaseModel):
    results: List[QueryResult]


@router.post("/querychat", response_model=QueryChatResponse, tags=["QueryChat"])
async def query_chat(
    request: QueryChatRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    RAG Retrieval Endpoint:
    1. Embed user query
    2. Search vector DB
    3. Return most relevant chunks
    """

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_embedding = embed_chunks([{"chunk_text": request.query}])[0]

    rows = await query_similar_chunks(
        session,
        query_embedding,
        request.top_k
    )

    results = [
        QueryResult(
            document_id=row[0].document_id,
            chunk_index=row[0].chunk_index,
            chunk_text=row[0].chunk_text,
            similarity=float(row[1]),
        )
        for row in rows
    ]

    return QueryChatResponse(results=results)