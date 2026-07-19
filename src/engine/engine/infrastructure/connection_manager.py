from redis.asyncio import from_url
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from engine.config import Settings
from engine.database.cache import RedisCacheManager
from engine.database.event import RedisStreamManager
from engine.database.relational import TimescaleSessionManager


class ConnectionManager:
    """Manages the connection of heavy TCP pools for the application."""

    def __init__(self, settings: Settings) -> None:
        """Initializes connection pools without opening execution sessions.

        Args:
            settings: Config object with required credentials.
        """
        self._engine = create_async_engine(url=settings.DB_URL, echo=False, pool_pre_ping=True)
        self._session_maker = async_sessionmaker(bind=self._engine, autocommit=False)

        self._redis_client = from_url(url=settings.REDIS_URL, decode_responses=True)

    def get_db_manager(self) -> TimescaleSessionManager:
        """Returns an adapter for relational operations."""
        return TimescaleSessionManager(self._session_maker)

    def get_cache_manager(self) -> RedisCacheManager:
        """Returns an adapter for cache operations."""
        return RedisCacheManager(self._redis_client)

    def get_event_manager(self) -> RedisStreamManager:
        """Returns an adapter for pub/sub event operations."""
        return RedisStreamManager(self._redis_client)

    async def close(self) -> None:
        """Gracefully shuts down all connection pools."""
        await self._engine.dispose()
        await self._redis_client.aclose()
