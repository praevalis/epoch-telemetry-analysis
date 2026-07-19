from typing import Any, cast

from redis.asyncio import Redis

from .interfaces import ICacheManager


class RedisCacheManager(ICacheManager):
    """Concrete Redis implementation for ICacheManager protocol."""

    def __init__(self, client: Redis) -> None:
        """Initializes the cache manager.

        Args:
            client: A pre-configured redis client.
        """
        self._client = client

    async def get_mapping(self, key: str) -> dict[str, str] | None:
        """Retrieves a hash mapping from Redis.

        Args:
            key: Key used for lookup.

        Returns:
            The dictionary if found, None if the cache misses.
        """
        result = await self._client.hgetall(key)

        if not result:
            return None

        return cast(dict[str, str], result)

    async def set_mapping(self, key: str, mapping: dict[str, str], ttl: int = 36000) -> None:
        """Stores a mapping atomically using a transaction pipeline.

        Args:
            key: The target cache key.
            mapping: The dictionary data to store.
            ttl: Time-to-Live in seconds. Defaults to 10 hours.
        """
        async with self._client.pipeline(transaction=True) as pipe:
            pipe.hset(key, mapping=cast(Any, mapping))
            pipe.expire(key, ttl)
            await pipe.execute()

    async def invalidate_mapping(self, key: str) -> None:
        """Removes a key from cache.

        Args:
            key: The target key to be removed.
        """
        # Using `unlink` instead of `delete` to prevent blocking the event loop
        await self._client.unlink(key)
