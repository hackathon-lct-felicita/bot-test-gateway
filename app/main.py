import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.logging_setup import configure_logging
from app.middleware.headers import HeadersMiddleware
from app.middleware.metrics import MetricsMiddleware

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Bot Test Gateway",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(HeadersMiddleware)
    app.add_middleware(MetricsMiddleware)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "healthy"}

    app.include_router(router, prefix="/api")

    return app


app = create_app()
