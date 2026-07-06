from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.shared.config import ApiSettings


def configure_cors(app: FastAPI, settings: ApiSettings) -> None:
    """Adds CORS middleware to FastAPI application.

    Args:
        app: FastAPI application.
        settings: Application config.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
        allow_headers=['Authorization', 'Content-Type', 'Accept'],
    )
