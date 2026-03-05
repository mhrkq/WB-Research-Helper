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
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..query.query_pipeline import run_query
from ..query.schemas import QueryRequest, QueryResponse
from ..utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/querychat", response_model=QueryResponse, tags=["QueryChat"])
async def query_chat(
    request: QueryRequest,
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