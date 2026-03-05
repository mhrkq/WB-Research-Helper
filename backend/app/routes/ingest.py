# backend/app/routes/ingest.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from ..ingest.ingest_pipeline import run_ingestion
from ..utils.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


class IngestRequest(BaseModel):
    url: HttpUrl


class IngestResponse(BaseModel):
    status: str
    document_id: int
    chunks: int


@router.post("/ingest", response_model=IngestResponse, tags=["Ingest"])
async def ingest_document(request: IngestRequest):
    """
    Ingest a web page URL:
    1. Crawl the URL
    2. Split content into chunks
    3. Generate embeddings
    4. Save everything to the database
    """
    try:
        result = await run_ingestion(str(request.url))
        logger.info(f"Ingestion completed for URL: {request.url}")
        return result
    except Exception as e:
        logger.error(f"Ingestion failed for URL {request.url}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")