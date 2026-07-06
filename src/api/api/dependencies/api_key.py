from typing import Annotated

from fastapi import Depends

from engine.application.api_key_service import ApiKeyService
from engine.database.cache import ICacheManager
from engine.database.relational import DbSession
from engine.domain.api_key import IApiKeyRepository
from engine.domain.common import ITransactionManager
from engine.repositories.api_key import ApiKeyRepository
from engine.repositories.cached_api_key import CachedApiKeyRepository

from .core import get_cache_manager, get_db_session, get_tx_manager


def get_api_key_repo(session: Annotated[DbSession, Depends(get_db_session)]) -> IApiKeyRepository:
    """Dependency for API key repository."""
    return ApiKeyRepository(session)


def get_cached_api_key_repo(
    api_key_repo: Annotated[IApiKeyRepository, Depends(get_api_key_repo)],
    cache_manager: Annotated[ICacheManager, Depends(get_cache_manager)],
) -> IApiKeyRepository:
    """Dependency for cached API key repository."""
    return CachedApiKeyRepository(api_key_repo, cache_manager, 1800)


def get_api_key_service(
    cached_api_key_repo: Annotated[IApiKeyRepository, Depends(get_cached_api_key_repo)],
    tx_manager: Annotated[ITransactionManager, Depends(get_tx_manager)],
) -> ApiKeyService:
    """Dependency for API key service."""
    return ApiKeyService(cached_api_key_repo, tx_manager)
