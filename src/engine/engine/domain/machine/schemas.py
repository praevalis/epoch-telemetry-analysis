from datetime import datetime
from typing import Literal
from uuid import UUID

from engine.domain.common import BaseDomainModel, BaseQueryModel


class MachineCreate(BaseDomainModel):
    name: str
    description: str | None = None


class MachineUpdate(BaseDomainModel):
    name: str | None = None
    description: str | None = None


class MachineResponse(BaseDomainModel):
    id: UUID
    name: str
    description: str | None
    is_active: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MachineFilterParams(BaseQueryModel):
    is_active: bool | None = None
    search: str | None = None
    sort_by: Literal['name', 'created_at', 'updated_at'] = 'created_at'
