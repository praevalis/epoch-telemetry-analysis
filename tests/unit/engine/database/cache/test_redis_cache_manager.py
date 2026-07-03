from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis

from engine.database.cache import RedisCacheManager


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    """Creates a fake redis client."""
    mock_client = AsyncMock(spec=Redis)
    return mock_client


@pytest.fixture
def redis_cache_manager(mock_redis_client: AsyncMock) -> RedisCacheManager:
    """Injects a fake redis client into the RedisCacheManager."""
    return RedisCacheManager(client=mock_redis_client)


@pytest.mark.asyncio
class TestRedisCacheManager:
    """Tests cache client management and operations."""

    async def test_set_mapping_executes_pipeline(
        self, redis_cache_manager: RedisCacheManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling set_mapping executes both hset and expire operations
        using a pipeline."""
        mock_pipeline = AsyncMock()
        mock_pipeline.__aenter__.return_value = mock_pipeline
        mock_redis_client.pipeline.return_value = mock_pipeline

        target_key = 'test:key:123'
        mapping = {'id': 'test-id-1', 'status': 'SUCCESS'}
        ttl = 3600

        await redis_cache_manager.set_mapping(target_key, mapping, ttl)

        mock_redis_client.pipeline.assert_called_once()
        mock_pipeline.hset.assert_called_once_with(target_key, mapping=mapping)
        mock_pipeline.expire.assert_called_once_with(target_key, ttl)
        mock_pipeline.execute.assert_called_once()

    async def test_get_mapping_returns_dict_on_hit(
        self, redis_cache_manager: RedisCacheManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling get_mapping returns the expected data on hit."""
        expected_data = {'id': 'test-id-1', 'status': 'SUCCESS'}
        target_key = 'test:key:123'

        mock_hgetall = AsyncMock()
        mock_hgetall.return_value = expected_data
        mock_redis_client.hgetall = mock_hgetall

        result = await redis_cache_manager.get_mapping(target_key)

        mock_redis_client.hgetall.assert_called_once_with(target_key)
        assert result == expected_data

    async def test_get_mapping_returns_none_on_miss(
        self, redis_cache_manager: RedisCacheManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling get_mapping returns none on miss."""
        target_key = 'test:key:123'

        mock_hgetall = AsyncMock()
        mock_hgetall.return_value = {}
        mock_redis_client.hgetall = mock_hgetall

        result = await redis_cache_manager.get_mapping(target_key)

        mock_redis_client.hgetall.assert_called_once_with(target_key)
        assert result is None

    async def test_invalidate_mapping_calls_delete(
        self, redis_cache_manager: RedisCacheManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling invalidate_mapping removes the key from cache."""
        target_key = 'test:key:123'
        mock_redis_client.unlink = AsyncMock()

        await redis_cache_manager.invalidate_mapping(target_key)

        mock_redis_client.unlink.assert_called_once_with(target_key)
