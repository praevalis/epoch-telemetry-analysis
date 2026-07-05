from uuid import UUID

from engine.database.cache import ICacheManager
from engine.database.relational.models import ApiKeyStatusEnum
from engine.domain.api_key import (
    ApiKeyCreate,
    ApiKeyFilterParams,
    ApiKeyResponse,
    IApiKeyRepository,
)


class CachedApiKeyRepository(IApiKeyRepository):
    """Decorator repository to handle caching for ApiKeyRepository."""

    def __init__(self, db_repo: IApiKeyRepository, cache_manager: ICacheManager, ttl: int) -> None:
        """Initializes the cached repository.

        Args:
            db_repo: Database repository to be wrapped over.
            cache_manager: Handles cache operations.
            ttl: Time-to-Live for cached data.
        """
        self.db_repo = db_repo
        self.cache = cache_manager
        self.ttl = ttl

    def _get_cache_key(self, key_hash: str) -> str:
        return f'apikey:hash:{key_hash}'

    async def get_by_hash(self, key_hash: str) -> ApiKeyResponse:
        """Retrieves an API key by hash. Attempts to fetch from cache,
        falls back to DB on miss.

        Args:
            key_hash: Hash for the API key.

        Returns:
            Retrieved API key.
        """
        cache_key = self._get_cache_key(key_hash)

        cached_mapping = await self.cache.get_mapping(cache_key)
        if cached_mapping:
            return ApiKeyResponse.model_validate(cached_mapping)

        db_key = await self.db_repo.get_by_hash(key_hash)
        dumped_data = db_key.model_dump(mode='json')
        mapping = {k: str(v) for k, v in dumped_data.items() if v is not None}

        await self.cache.set_mapping(cache_key, mapping, self.ttl)

        return db_key

    async def revoke(self, key_id: UUID) -> ApiKeyResponse:
        """Revokes API key and purges cache.

        Args:
            key_id: ID of the key to revoke.

        Returns:
            Revoked API key.
        """
        revoked_key = await self.db_repo.revoke(key_id)

        cache_key = self._get_cache_key(revoked_key.key_hash)
        await self.cache.invalidate_mapping(cache_key)

        return revoked_key

    async def revoke_for_machine(self, machine_id: UUID) -> None:
        """Invalidates cached keys for a machine and then revokes them.

        Args:
            machine_id: ID of the machine.
        """
        keys_to_revoke = await self.db_repo.get_many_for_machine(
            machine_id, ApiKeyFilterParams(status=ApiKeyStatusEnum.ACTIVE)
        )

        for key in keys_to_revoke:
            await self.cache.invalidate_mapping(self._get_cache_key(key.key_hash))

        await self.db_repo.revoke_for_machine(machine_id)

    # Pass through methods, these operations do not require cache handling.
    async def create(self, payload: ApiKeyCreate) -> ApiKeyResponse:
        return await self.db_repo.create(payload)

    async def get_by_id(self, key_id: UUID) -> ApiKeyResponse:
        return await self.db_repo.get_by_id(key_id)

    async def get_many_for_machine(
        self, machine_id: UUID, filter_params: ApiKeyFilterParams
    ) -> list[ApiKeyResponse]:
        return await self.db_repo.get_many_for_machine(machine_id, filter_params)
