from typing import Protocol
from uuid import UUID

from .schemas import ApiKeyCreate, ApiKeyFilterParams, ApiKeyResponse


class IApiKeyRepository(Protocol):
    """Abstract interface for api key data operations."""

    async def create(self, payload: ApiKeyCreate) -> ApiKeyResponse:
        """Create API key.

        Args:
            payload: Hashed key and metadata for the API key.

        Returns:
            Created API key.
        """
        ...

    async def get_by_id(self, key_id: UUID) -> ApiKeyResponse:
        """Retrieves an API key using the provided ID.

        Args:
            key_id: ID of the API key.

        Returns:
            Retrieved API key.

        Raises:
            ApiKeyNotFoundError: When a key with the specified ID is not found.
            ApiKeyRevokedError: If the key with the given ID is revoked.
        """
        ...

    async def get_by_hash(self, key_hash: str) -> ApiKeyResponse:
        """Retrieves an API key using the provided hash.

        Args:
            key_hash: Hash of the API key.

        Returns:
            Retrieved API key.

        Raises:
            ApiKeyNotFoundError: When a key with the hash is not found.
            ApiKeyRevokedError: If the key with the given hash is revoked.
        """
        ...

    async def get_many_for_machine(
        self, machine_id: UUID, filter_params: ApiKeyFilterParams
    ) -> tuple[list[ApiKeyResponse], int]:
        """Retrieves API keys for the given machine and filter params.

        Args:
            machine_id: ID of the machine.
            filter_params: Filter criteria.

        Returns:
            Retrieved API keys and the total number of keys.
        """
        ...

    async def revoke(self, key_id: UUID) -> ApiKeyResponse:
        """Revokes API key with the given ID.

        Args:
            key_id: ID of the key.

        Returns:
            Revoked API key.

        Raises:
            ApiKeyNotFoundError: When the key with given ID is not present.
            ApiKeyRevokedError: If the API key is already revoked.
        """
        ...

    async def revoke_for_machine(self, machine_id: UUID) -> None:
        """Revokes all active API keys associated with the machine.

        Args:
            machine_id: ID of the machine.

        Returns:
            No response is returned.
        """
        ...
