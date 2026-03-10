# backend/app/main.py

import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.logger import setup_logger
from app.routes.health import router as health_router
from app.routes.ingest import router as ingest_router
from app.routes.documents import router as documents_router
from app.routes.querychat import router as querychat_router
from app.db.database import init_db, engine
from app.config import get_settings

settings = get_settings()
logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    logger.info("Starting application")

    # if settings.ENVIRONMENT != "production":
    #     await init_db()
    await init_db()

    try:
        yield
    finally:
        logger.info("Shutting down application")
        await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
)

# CORS
if settings.ENVIRONMENT == "development":
    cors_origins = settings.LOCALHOST_CORS_ORIGINS
else:
    cors_origins = settings.CORS_ORIGINS  # production-specific list

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(ingest_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(querychat_router, prefix=settings.API_PREFIX)

logger.info("Application routes configured")