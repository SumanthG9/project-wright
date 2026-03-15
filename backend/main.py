from contextlib import asynccontextmanager
from venv import logger

import structlog
from fastapi import FastAPI

from backend.auth.router import router as auth_router
from backend.core.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info(
        "wright.startup",
        environment=settings.environment,
        pipeline_mode=settings.pipeline_mode,
    )
    # Database connection pools will be initialised here in Week 4
    yield
    # ── Shutdown ─────────────────────────────────────────────
    logger.info("wright.shutdown")
    # Connection pools will be closed here in Week 4


app = FastAPI(
    title="Project Wright API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.include_router(auth_router, prefix="/auth")


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "pipeline_mode": settings.pipeline_mode,
    }
