import logging
from typing import cast

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from engine.domain.api_key import ApiKeyNotFoundError, ApiKeyRevokedError
from engine.domain.common import DomainException
from engine.domain.machine import MachineAlreadyExistsError, MachineNotFoundError

logger = logging.getLogger(__name__)

EXCEPTION_REGISTRY: dict[type[DomainException], tuple[int, str]] = {
    MachineAlreadyExistsError: (status.HTTP_409_CONFLICT, 'machine_already_exists'),
    MachineNotFoundError: (status.HTTP_404_NOT_FOUND, 'machine_not_found'),
    ApiKeyNotFoundError: (status.HTTP_401_UNAUTHORIZED, 'api_key_not_found'),
    ApiKeyRevokedError: (status.HTTP_401_UNAUTHORIZED, 'api_key_not_found'),
    # NOTE: Deliberately using the same status code and error message for revocation error
}


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translates any registered domain exception into standardized HTTP response."""
    exc = cast(DomainException, exc)

    status_code, error_code = EXCEPTION_REGISTRY[type(exc)]

    logger.error(
        f'Domain exception intercepted - Code: {error_code} | '
        f'Path: {request.url.path} | Method: {request.method} | Details: {exc.message}'
    )

    return JSONResponse(
        status_code=status_code, content={'error': error_code, 'message': exc.message}
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Binds all domain exception handlers to the FastAPI application.

    Args:
        app: FastAPI app instance.
    """
    for exc in EXCEPTION_REGISTRY:
        app.add_exception_handler(exc, generic_exception_handler)
