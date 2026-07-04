from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseDomainModel(BaseModel):
    """Base model for all domain schemas.

    Enforces strict payload validation and JSON camelCase convention.
    """

    model_config = ConfigDict(
        extra='forbid',  # Rejects payloads with unknown fields
        populate_by_name=True,  # Allows creating models using both snake_case and camelCase
        alias_generator=to_camel,  # Automatically converts snake_case fields to camelCase for JSON
        from_attributes=True,  # Allows initializing Pydantic models from SQLAlchemy objects
    )


class BaseQueryModel(BaseModel):
    """Base for model query parameters."""

    model_config = ConfigDict(
        extra='ignore',  # Ignores extra params
        populate_by_name=True,
    )

    limit: int = 50
    offset: int = 0
    sort_dir: Literal['asc', 'desc'] = 'desc'
