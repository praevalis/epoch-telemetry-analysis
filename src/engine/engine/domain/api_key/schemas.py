from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import Field

from engine.domain.common import BaseDomainModel, BaseQueryModel


class ApiKeyStatusEnum(StrEnum):
    ACTIVE = 'ACTIVE'
    REVOKED = 'REVOKED'


class ApiKeyCreateMetadata(BaseDomainModel):
    name: str
    machine_id: UUID


class ApiKeyCreate(ApiKeyCreateMetadata):
    key_hash: str
    masked_key: str


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


class ApiKeyRawResponse(ApiKeyResponse):
    raw_key: str


class ApiKeyFilterParams(BaseQueryModel):
    status: ApiKeyStatusEnum | None = ApiKeyStatusEnum.ACTIVE
    search: str | None = None
    sort_by: Literal['created_at', 'updated_at', 'revoked_at'] = 'created_at'
