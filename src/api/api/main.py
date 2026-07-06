import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.exceptions import register_exception_handlers
from api.middlewares import configure_cors
from api.routes import v1_router
from api.shared.config import get_api_settings
from api.shared.logging import configure_logging
from engine.infrastructure import ConnectionManager

logger = logging.getLogger(__name__)

configure_logging()
settings = get_api_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles app lifecycle events (startup, shutdown)."""
    manager = None

    try:
        logger.info('Initializing TCP connection pools.')

        manager = ConnectionManager(settings)
        app.state.connections = manager

        logger.info('Successfully initialized TCP connection pools.')

        yield
    finally:
        if manager is not None:
            await manager.close()
            logger.info('Successfully closed TCP connection pools.')


def create_app() -> FastAPI:
    """Factory function for FastAPI app."""
    app = FastAPI(lifespan=lifespan)

    register_exception_handlers(app)
    configure_cors(app, settings)

    app.include_router(v1_router)

    return app


app = create_app()
