from functools import lru_cache

from pydantic import field_validator

from engine.config import Settings


class ApiSettings(Settings):
    ALLOWED_ORIGINS: str | list[str] = 'http://localhost:5173'

    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        elif isinstance(v, list):
            return v
        else:
            raise TypeError(f'Invalid type for ALLOWED_ORIGINS variable: {type(v)}')


@lru_cache(maxsize=1)
def get_api_settings() -> ApiSettings:
    """Dependency that caches and returns API configuration."""
    return ApiSettings()
