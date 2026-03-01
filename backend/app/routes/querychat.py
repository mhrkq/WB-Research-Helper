# backend/routes/querychat.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.db.database import get_db
from app.ingest.repositories import query_similar_chunks
from app.ingest.services.embedder import embed_chunks

from app.llm.chat_service import generate_answer

router = APIRouter()


class QueryChatRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[int] = None
    title_contains: Optional[str] = None


class QueryResult(BaseModel):
    document_id: int
    chunk_index: int
    chunk_text: str
    similarity: float


class QueryChatResponse(BaseModel):
    answer: str
    results: List[QueryResult]


@router.post("/querychat", response_model=QueryChatResponse, tags=["QueryChat"])
async def query_chat(
    request: QueryChatRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Full RAG Endpoint:
    1. Embed user query
    2. Search vector DB
    3. Send top chunks to LLM
    4. Return llm answer + top chunks
    """

    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    query_embedding = embed_chunks(
        [{"chunk_text": request.query}]
    )[0]

    # retrieve similar chunks
    rows = await query_similar_chunks(
        session,
        query_embedding,
        request.top_k,
        document_id=request.document_id,
        title_contains=request.title_contains,
    )

    if not rows:
        raise HTTPException(status_code=404, detail="No relevant documents found")

    # extract chunk texts for LLM
    chunk_texts = [row[0].chunk_text for row in rows]

    answer = await generate_answer(request.query, chunk_texts)

    results = [
        QueryResult(
            document_id=row[0].document_id,
            chunk_index=row[0].chunk_index,
            chunk_text=row[0].chunk_text,
            similarity=float(row[1]),
        )
        for row in rows
    ]

    return QueryChatResponse(
        answer=answer,
        results=results
    )