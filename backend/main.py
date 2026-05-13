from contextlib import asynccontextmanager
from venv import logger

import structlog
from fastapi import FastAPI

from backend.auth.router import router as auth_router
from backend.core.config import settings
from backend.projects.router import router as projects_router
from backend.uploads.router import router as uploads_router
from backend.ws.router import router as ws_router

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
app.include_router(projects_router, prefix="/projects")
app.include_router(uploads_router, prefix="/uploads")
app.include_router(ws_router, prefix="/ws")


@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
        "pipeline_mode": settings.pipeline_mode,
    }
