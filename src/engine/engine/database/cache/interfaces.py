from typing import Protocol


class ICacheManager(Protocol):
    """Generic contract for cache operations."""

    async def get_mapping(self, key: str) -> dict[str, str] | None:
        """Retrieves a dictionary mapping for a given key."""
        ...

    async def set_mapping(self, key: str, mapping: dict[str, str], ttl: int) -> None:
        """Stores a dictionary mapping with an expiration time."""
        ...

    async def invalidate_mapping(self, key: str) -> None:
        """Removes a key from cache."""
        ...
