from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID

from engine.domain.api_key import (
    ApiKeyCreate,
    ApiKeyCreateMetadata,
    ApiKeyFilterParams,
    ApiKeyRawResponse,
    ApiKeyResponse,
    ApiKeyRevokedError,
    ApiKeyStatusEnum,
    IApiKeyRepository,
)
from engine.domain.common import ITransactionManager


class ApiKeyService:
    """Handles business logic for API key domain."""

    def __init__(
        self,
        api_key_repo: IApiKeyRepository,
        tx_manager: ITransactionManager,
    ) -> None:
        """Initializes the service.

        Args:
            api_key_repo: Repository that handles api key-related data operations.
            tx_manager: Cross-domain transaction manager.
        """
        self.api_key_repo = api_key_repo
        self.tx_manager = tx_manager

    async def create_api_key(self, payload: ApiKeyCreateMetadata) -> ApiKeyRawResponse:
        """Generates static API key and persists it in database.

        Args:
            payload: Metadata for creating the API key.

        Returns:
            API key data and raw key for one-time display.
        """
        raw_key = f'sk_{token_urlsafe(32)}'
        key_hash = sha256(raw_key.encode('utf-8')).hexdigest()
        masked_key = f'{raw_key[:5]}{"." * 8}{raw_key[-4:]}'  # Used for safe display post creation

        created_api_key = await self.api_key_repo.create(
            ApiKeyCreate(
                key_hash=key_hash,
                name=payload.name,
                machine_id=payload.machine_id,
                masked_key=masked_key,
            )
        )
        await self.tx_manager.commit()

        return ApiKeyRawResponse(**created_api_key.model_dump(), raw_key=raw_key)

    async def verify_api_key(self, raw_key: str) -> ApiKeyResponse:
        """Verifies provided raw key and returns associated data.

        Args:
            raw_key: Key to verify.

        Returns:
            Verified API key details.

        Raises:
            ApiKeyRevokedError: If the provided API key is revoked.
        """
        key_hash = sha256(raw_key.encode('utf-8')).hexdigest()
        api_key = await self.get_api_key_by_hash(key_hash)

        if api_key.status == ApiKeyStatusEnum.REVOKED:
            raise ApiKeyRevokedError(api_key.id)

        return api_key

    async def get_api_key_by_id(self, key_id: UUID) -> ApiKeyResponse:
        """Retrieves an API key by ID.

        Args:
            key_id: ID of the API key.

        Returns:
            ApiKeyResponse: Retrieved API key without sensitive data.
        """
        return await self.api_key_repo.get_by_id(key_id)

    async def get_api_key_by_hash(self, key_hash: str) -> ApiKeyResponse:
        """Retrieves an API key by hash.

        Args:
            key_hash: Hash of the API key.

        Returns:
            ApiKeyResponse: Retrieved API key without sensitive data.
        """
        return await self.api_key_repo.get_by_hash(key_hash)

    async def get_api_keys_for_machine(
        self, machine_id: UUID, filter_params: ApiKeyFilterParams
    ) -> list[ApiKeyResponse]:
        """Retrieves API keys associated with the machine that fulfill
        filter criteria.

        Args:
            machine_id: ID of the machine.
            filter_params: Filter criteria.

        Returns:
            Retrieved API keys.
        """
        return await self.api_key_repo.get_many_for_machine(machine_id, filter_params)

    async def revoke_api_key(self, key_id: UUID) -> None:
        """Revokes active API key by ID.

        Args:
            key_id: ID of the key to be revoked.

        Returns:
            No response is returned after successful revocation.
        """
        await self.api_key_repo.revoke(key_id)
        await self.tx_manager.commit()

    async def revoke_api_keys_for_machine(self, machine_id: UUID) -> None:
        """Revokes active API keys associated with a machine.

        Args:
            machine_id: ID of the machine.

        Returns:
            No response is returned after successful revocation.
        """
        await self.api_key_repo.revoke_for_machine(machine_id)
        await self.tx_manager.commit()
