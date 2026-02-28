# repositories.py

# insert md and embeddings to postgreSQL

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from ..db.models import WBResearchDocument, DocumentChunk
from ..db.database import get_db
from pgvector.sqlalchemy import Vector

async def save_md(session: AsyncSession, url: str, md_content: str, title: str = None) -> int:
    """
    Save raw markdown document to the database.
    Returns the document_id for linking chunks.
    """
    doc = WBResearchDocument(
        url=str(url),
        markdown_content=md_content,
        title=title
    )
    session.add(doc)
    try:
        await session.commit()
        await session.refresh(doc)  # refresh to get id
        return doc.id
    except IntegrityError:
        # means document with this URL already exists
        await session.rollback()
        existing_doc = await session.execute(
            select(WBResearchDocument).where(WBResearchDocument.url == url)
        )
        doc_obj = existing_doc.scalar_one()
        return doc_obj.id

async def get_document_by_id(session: AsyncSession, document_id: int) -> WBResearchDocument:
    """Fetch a document by its ID."""
    result = await session.execute(
        select(WBResearchDocument).where(WBResearchDocument.id == document_id)
    )
    return result.scalar_one_or_none()

async def save_embeddings(
    session: AsyncSession,
    document_id: int,
    chunks: List[str],
    embeddings: List[List[float]],
):
    """
    Save chunks and embeddings to the database, linked to a document_id.
    Assumes chunks[i] corresponds to embeddings[i].
    """

    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks and embeddings must match.")

    chunk_objects = [
        DocumentChunk(
            document_id=document_id,
            chunk_index=idx,
            chunk_text=chunk_text,
            embedding=vector
        )
        for idx, (chunk_text, vector) in enumerate(zip(chunks, embeddings))
    ]

    try:
        session.add_all(chunk_objects)
        await session.commit()
    except Exception:
        await session.rollback()
        raise


async def get_chunks_by_document(session: AsyncSession, document_id: int) -> List[DocumentChunk]:
    """Fetch all chunks for a given document."""
    result = await session.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
    )
    return result.scalars().all()