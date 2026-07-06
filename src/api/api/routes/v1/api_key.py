from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.api_key import get_api_key_service
from api.schemas.pagination import PaginationResponse
from engine.application.api_key_service import ApiKeyService
from engine.domain.api_key import (
    ApiKeyCreateMetadata,
    ApiKeyFilterParams,
    ApiKeyRawResponse,
    ApiKeyResponse,
)

router = APIRouter(prefix='/api-keys', tags=['API Keys'])


@router.post('', response_model=ApiKeyRawResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: ApiKeyCreateMetadata,
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """Creates a new API key.

    Returns the raw secret key payload.
    """
    return await api_key_service.create_api_key(payload)


@router.get('/machine/{machine_id}', response_model=PaginationResponse[ApiKeyResponse])
async def get_machine_api_keys(
    machine_id: UUID,
    filter_params: Annotated[ApiKeyFilterParams, Depends()],
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """Retrieves a paginated list of API keys associated with a specific machine."""

    api_keys, total = await api_key_service.get_api_keys_for_machine(machine_id, filter_params)

    return PaginationResponse(
        items=api_keys,
        total=total,
        limit=filter_params.limit,
        offset=filter_params.offset,
    )


@router.get('/{api_key_id}', response_model=ApiKeyResponse)
async def get_api_key(
    api_key_id: UUID,
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """Retrieves a specific API key by its identifier."""
    return await api_key_service.get_api_key_by_id(api_key_id)


@router.delete('/{api_key_id}', status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    api_key_id: UUID,
    api_key_service: Annotated[ApiKeyService, Depends(get_api_key_service)],
):
    """Revokes an API key, instantly invalidating it for future use."""
    await api_key_service.revoke_api_key(api_key_id)
