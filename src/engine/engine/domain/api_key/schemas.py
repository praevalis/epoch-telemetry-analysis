from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from engine.database.relational.models import ApiKeyStatusEnum
from engine.domain.common import BaseDomainModel, BaseQueryModel


class ApiKeyCreate(BaseDomainModel):
    key_hash: str
    name: str
    masked_key: str
    machine_id: UUID


class ApiKeyResponse(BaseDomainModel):
    id: UUID
    key_hash: str = Field(exclude=True)
    name: str
    masked_key: str
    machine_id: UUID
    status: ApiKeyStatusEnum
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ApiKeyFilterParams(BaseQueryModel):
    status: ApiKeyStatusEnum | None = ApiKeyStatusEnum.ACTIVE
    search: str | None = None
    sort_by: Literal['created_at', 'updated_at', 'revoked_at'] = 'created_at'
