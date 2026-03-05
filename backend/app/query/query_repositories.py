# backend/app/query/query_repositories.py

# retrieve documents
# search similar chunks

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from ..db.models import WBResearchDocument, DocumentChunk
from ..db.database import get_db
from pgvector.sqlalchemy import Vector

from sqlalchemy import text
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.orm import selectinload

async def get_document_by_id(session: AsyncSession, document_id: int) -> WBResearchDocument:
    """Fetch a document by its ID."""
    result = await session.execute(
        select(WBResearchDocument).where(WBResearchDocument.id == document_id)
    )
    return result.scalar_one_or_none()

async def get_chunks_by_document(session: AsyncSession, document_id: int) -> List[DocumentChunk]:
    """Fetch all chunks for a given document."""
    result = await session.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document_id).order_by(DocumentChunk.chunk_index)
    )
    return result.scalars().all()

async def query_similar_chunks(
    session,
    query_embedding: list[float],
    top_k: int = 5,
    document_id = None,
    title_contains = None,
):
    """
    Perform cosine similarity search using pgvector comparator, with optional document filtering.
    """

    # when fetching chunk, also fetch its document
    stmt = (
        select(
            DocumentChunk,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("similarity")
        )
        .options(selectinload(DocumentChunk.document))
    )

    if title_contains:
        stmt = stmt.join(WBResearchDocument, WBResearchDocument.id == DocumentChunk.document_id)
    
    # apply filters conditionally
    if document_id is not None:
        stmt = stmt.where(DocumentChunk.document_id == document_id)
    
    if title_contains:
        stmt = stmt.where(WBResearchDocument.title.ilike(f"%{title_contains}%"))

    # Order by similarity (ascending distance)
    stmt = stmt.order_by("similarity").limit(top_k)

    # List[Tuple[DocumentChunk, float]]
    # a list of rows, each containing (DocumentChunk, cosine_distance_float)
    rows = await session.execute(stmt)
    return rows.all()