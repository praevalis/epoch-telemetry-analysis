from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from engine.database.relational.models import ApiKey
from engine.domain.api_key import (
    ApiKeyCreate,
    ApiKeyFilterParams,
    ApiKeyNotFoundError,
    ApiKeyResponse,
    ApiKeyRevokedError,
    ApiKeyStatusEnum,
    IApiKeyRepository,
)


class ApiKeyRepository(IApiKeyRepository):
    """Concrete implementation for API key data operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes API key repository.

        Args:
            session: Injected SQLAlchemy session.
        """
        self.session = session

    async def create(self, payload: ApiKeyCreate) -> ApiKeyResponse:
        """Create API key.

        Args:
            payload: Hashed key and metadata for the API key.

        Returns:
            Created API key.
        """
        api_key = ApiKey(**payload.model_dump())
        self.session.add(api_key)

        await self.session.flush()
        await self.session.refresh(api_key)

        return ApiKeyResponse.model_validate(api_key)

    async def get_by_id(self, key_id: UUID) -> ApiKeyResponse:
        """Retrieves an API key using the provided ID. Returns both
        active and revoked keys, the service layer is responsible for
        handling revoked keys.

        Args:
            key_id: ID of the API key.

        Returns:
            Retrieved API key.

        Raises:
            ApiKeyNotFoundError: When a key with the specified ID is not found.
        """
        stmt = select(ApiKey).where(ApiKey.id == key_id)

        try:
            result = await self.session.execute(stmt)
            api_key = result.scalar_one()

        except NoResultFound as e:
            raise ApiKeyNotFoundError(key_id) from e

        return ApiKeyResponse.model_validate(api_key)

    async def get_by_hash(self, key_hash: str) -> ApiKeyResponse:
        """Retrieves an API key using the provided hash. Returns both
        active and revoked keys, the service layer is responsible for
        handling revoked keys.

        Args:
            key_hash: Hash of the API key.

        Returns:
            Retrieved API key.

        Raises:
            ApiKeyNotFoundError: When a key with the hash is not found.
        """
        stmt = select(ApiKey).where(ApiKey.key_hash == key_hash)

        try:
            result = await self.session.execute(stmt)
            api_key = result.scalar_one()

        except NoResultFound as e:
            raise ApiKeyNotFoundError(key_hash=key_hash) from e

        return ApiKeyResponse.model_validate(api_key)

    async def get_many_for_machine(
        self, machine_id: UUID, filter_params: ApiKeyFilterParams
    ) -> list[ApiKeyResponse]:
        """Retrieves API keys for the given machine and filter params.

        Args:
            machine_id: ID of the machine.
            filter_params: Filter criteria.

        Returns:
            Retrieved API keys.
        """
        stmt = select(ApiKey).where(ApiKey.machine_id == machine_id)

        if filter_params.status is not None:
            stmt = stmt.where(ApiKey.status == filter_params.status)
        else:
            stmt = stmt.where(ApiKey.status == ApiKeyStatusEnum.ACTIVE)

        if filter_params.search:
            search_term = f'%{filter_params.search}%'
            stmt = stmt.where(ApiKey.name.ilike(search_term))

        sort_column = getattr(ApiKey, filter_params.sort_by)
        if filter_params.sort_dir == 'asc':
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        stmt = stmt.limit(filter_params.limit).offset(filter_params.offset)
        result = await self.session.execute(stmt)
        api_keys = result.scalars().all()

        return [ApiKeyResponse.model_validate(k) for k in api_keys]

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
        stmt = select(ApiKey).where(ApiKey.id == key_id)
        result = await self.session.execute(stmt)
        api_key = result.scalar_one_or_none()

        if not api_key:
            raise ApiKeyNotFoundError(key_id=key_id)

        if api_key.status == ApiKeyStatusEnum.REVOKED:
            raise ApiKeyRevokedError(key_id)

        api_key.status = ApiKeyStatusEnum.REVOKED
        api_key.revoked_at = func.now()

        await self.session.flush()
        await self.session.refresh(api_key)

        return ApiKeyResponse.model_validate(api_key)

    async def revoke_for_machine(self, machine_id: UUID) -> None:
        """Revokes all active API keys associated with the machine.

        Args:
            machine_id: ID of the machine.

        Returns:
            No response is returned.
        """
        stmt = (
            update(ApiKey)
            .where(ApiKey.machine_id == machine_id, ApiKey.status == ApiKeyStatusEnum.ACTIVE)
            .values(status=ApiKeyStatusEnum.REVOKED, revoked_at=func.now())
        )

        await self.session.execute(stmt)
        await self.session.flush()
