# backend/routes/querychat.py

# just like how backend/app/routes/ingest.py only run 1 func (run_ingestion from backend.app.ingest.ingest_pipeline),
# querychat.py should only run 1 func (run query from backend.app.query.query_pipeline)
# query_pipeline will
# - call query_similar_chunks
# - convert rows into structured dicts
# - call reranker_service
# - return final top_k chunks

# API route
#    ↓
# query_pipeline
#    ↓
# embedding_service
#    ↓
# retrieval_service
#    ↓
# rerank_service
#    ↓
# answer_service
#    ↓
# response

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..db.database import get_db
from ..query.query_pipeline import run_query
from ..utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class QueryChatRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[int] = None
    title_contains: Optional[str] = None


class QueryResult(BaseModel):
    document_id: int
    chunk_index: int
    chunk_text: str
    vector_similarity: float
    rerank_score: float


class QueryChatResponse(BaseModel):
    answer: str
    results: List[QueryResult]


@router.post("/querychat", response_model=QueryChatResponse, tags=["QueryChat"])
async def query_chat(
    request: QueryChatRequest,
    session: AsyncSession = Depends(get_db),
):
    """
    Full RAG endpoint.
    Delegates all logic to query_pipeline.run_query()
    """
    try:
        result = await run_query(
            session=session,
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            title_contains=request.title_contains,
        )

        logger.info(f"Query executed successfully: {request.query}")
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")