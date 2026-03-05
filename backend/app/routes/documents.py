from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ..db.database import get_db
from ..db.models import WBResearchDocument
# from backend.app.ingest.ingest_repositories import get_document_by_id, get_chunks_by_document
from ..query.query_repositories import get_document_by_id, get_chunks_by_document

router = APIRouter()


@router.get("/documents", tags=["Documents"])
async def list_documents(session: AsyncSession = Depends(get_db)):
    """
    Return all stored documents (without embeddings).
    """
    result = await session.execute(
        select(WBResearchDocument)
    )
    documents = result.scalars().all()

    return [
        {
            "id": doc.id,
            "url": doc.url,
            "title": doc.title
        }
        for doc in documents
    ]


@router.get("/documents/{document_id}", tags=["Documents"])
async def get_document(document_id: int, session: AsyncSession = Depends(get_db)):
    """
    Return full markdown content of a document.
    """
    doc = await get_document_by_id(session, document_id)

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "url": doc.url,
        "title": doc.title,
        "markdown_content": doc.markdown_content
    }


@router.get("/documents/{document_id}/chunks", tags=["Documents"])
async def get_document_chunks(document_id: int, session: AsyncSession = Depends(get_db)):
    """
    Return all chunks for a document (without embeddings).
    """
    chunks = await get_chunks_by_document(session, document_id)

    return [
        {
            "chunk_index": chunk.chunk_index,
            "chunk_text": chunk.chunk_text
        }
        for chunk in chunks
    ]