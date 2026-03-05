# backend/app/query/services/retrieval_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Tuple

from ..query_repositories import query_similar_chunks
from ...db.models import DocumentChunk


def convert_rows(rows: List[Tuple[DocumentChunk, float]]) -> List[Dict]:

    documents = []

    for chunk, similarity in rows:
        documents.append({
            "content": chunk.chunk_text,
            "title": chunk.document.title if chunk.document else None,
            "metadata": {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "similarity": float(similarity),
            }
        })

    return documents


async def retrieve_chunks(
    session: AsyncSession,
    query_embedding,
    top_k: int,
    document_id: Optional[int],
    title_contains: Optional[str],
):

    rows = await query_similar_chunks(
        session=session,
        query_embedding=query_embedding,
        top_k=top_k,
        document_id=document_id,
        title_contains=title_contains,
    )

    return convert_rows(rows)