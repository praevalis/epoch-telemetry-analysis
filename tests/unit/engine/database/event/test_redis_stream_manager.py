from typing import Literal
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis
from redis.exceptions import ResponseError

from engine.database.event.manager import RedisStreamManager


@pytest.fixture
def mock_redis_client() -> AsyncMock:
    """Creates a fake redis client."""
    mock_client = AsyncMock(spec=Redis)
    # Explicitly attach AsyncMocks because redis-py dynamically defines async commands
    # such that inspect.iscoroutinefunction() evaluates to False for them.
    mock_client.xadd = AsyncMock()
    mock_client.xreadgroup = AsyncMock()
    mock_client.xack = AsyncMock()
    mock_client.xnack = AsyncMock()
    mock_client.xgroup_create = AsyncMock()
    return mock_client


@pytest.fixture
def redis_event_manager(mock_redis_client: AsyncMock) -> RedisStreamManager:
    """Injects a fake redis client into the RedisStreamManager."""
    return RedisStreamManager(client=mock_redis_client)


@pytest.mark.asyncio
class TestRedisStreamManager:
    """Tests event broker management and operations."""

    async def test_publish_calls_xadd_with_defaults(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling publish executes xadd with default maxlen and approximate trimming."""
        expected_event_id = '171000000-0'
        mock_redis_client.xadd.return_value = expected_event_id

        target_topic = 'events:telemetry:raw'
        payload = {'cpu': 85.5, 'mem': 60.2}

        result = await redis_event_manager.publish(target_topic, payload)

        mock_redis_client.xadd.assert_called_once_with(
            name=target_topic,
            fields=payload,
            maxlen=100000,
            approximate=True,
        )
        assert result == expected_event_id

    async def test_publish_respects_custom_maxlen_kwarg(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling publish passes custom maxlen when provided via kwargs."""
        mock_redis_client.xadd.return_value = '171000000-1'

        target_topic = 'events:telemetry:raw'
        payload = {'cpu': 90.0}
        custom_maxlen = 500

        await redis_event_manager.publish(target_topic, payload, maxlen=custom_maxlen)

        mock_redis_client.xadd.assert_called_once_with(
            name=target_topic,
            fields=payload,
            maxlen=custom_maxlen,
            approximate=True,
        )

    async def test_ensure_group_calls_xgroup_create(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling ensure_group executes xgroup_create with mkstream set to true."""
        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'

        await redis_event_manager.ensure_group(target_topic, target_group)

        mock_redis_client.xgroup_create.assert_called_once_with(
            name=target_topic,
            groupname=target_group,
            id='0',
            mkstream=True,
        )

    async def test_ensure_group_suppresses_exceptions(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling ensure_group silently ignores exceptions if the group already exists."""
        mock_redis_client.xgroup_create.side_effect = ResponseError(
            'BUSYGROUP Consumer Group name already exists'
        )

        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'

        # Should not raise an exception
        await redis_event_manager.ensure_group(target_topic, target_group)
        mock_redis_client.xgroup_create.assert_called_once()

    async def test_consume_returns_parsed_events_on_hit(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling consume returns a list of decoded event tuples when messages exist."""
        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'
        consumer_id = 'worker-1'

        mock_redis_response = [
            (
                target_topic,
                [
                    (b'171000000-0', {'cpu': '85.5'}),
                    (b'171000000-1', {'cpu': '90.0'}),
                ],
            )
        ]
        mock_redis_client.xreadgroup.return_value = mock_redis_response

        results = await redis_event_manager.consume(
            topic=target_topic,
            group=target_group,
            consumer_id=consumer_id,
            batch_size=10,
            timeout_ms=1000,
        )

        mock_redis_client.xgroup_create.assert_called_once()
        mock_redis_client.xreadgroup.assert_called_once_with(
            groupname=target_group,
            consumername=consumer_id,
            streams={target_topic: '>'},
            count=10,
            block=1000,
        )
        assert results == [
            ('171000000-0', {'cpu': '85.5'}),
            ('171000000-1', {'cpu': '90.0'}),
        ]

    async def test_consume_returns_empty_list_on_miss(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling consume returns an empty list when no new messages exist."""
        mock_redis_client.xreadgroup.return_value = []

        results = await redis_event_manager.consume(
            topic='events:telemetry:raw',
            group='group:timescale_storage',
            consumer_id='worker-1',
        )

        mock_redis_client.xreadgroup.assert_called_once()
        assert results == []

    async def test_acknowledge_calls_xack(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling acknowledge executes xack with all provided event identifiers."""
        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'
        event_ids = ['171000000-0', '171000000-1']

        await redis_event_manager.acknowledge(target_topic, target_group, event_ids)

        mock_redis_client.xack.assert_called_once_with(
            target_topic, target_group, '171000000-0', '171000000-1'
        )

    async def test_acknowledge_does_nothing_when_ids_empty(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling acknowledge bypasses xack if the provided list is empty."""
        await redis_event_manager.acknowledge('events:telemetry:raw', 'group:timescale_storage', [])

        mock_redis_client.xack.assert_not_called()

    async def test_unacknowledge_defaults_to_retry_intent(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling unacknowledge without an intent defaults to retry (FAIL mode)."""
        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'
        event_ids = ['171000000-0', '171000000-1']

        await redis_event_manager.unacknowledge(target_topic, target_group, event_ids)

        mock_redis_client.xnack.assert_called_once_with(
            target_topic, target_group, 'FAIL', '171000000-0', '171000000-1'
        )

    @pytest.mark.parametrize(
        ('intent', 'expected_mode'),
        [
            ('retry', 'FAIL'),
            ('discard', 'FATAL'),
            ('reset', 'SILENT'),
        ],
    )
    async def test_unacknowledge_calls_xnack_with_mapped_mode(
        self,
        redis_event_manager: RedisStreamManager,
        mock_redis_client: AsyncMock,
        intent: Literal['retry', 'discard', 'reset'],
        expected_mode: str,
    ) -> None:
        """Tests calling unacknowledge maps intents to correct Redis recovery modes."""
        target_topic = 'events:telemetry:raw'
        target_group = 'group:timescale_storage'
        event_ids = ['171000000-0', '171000000-1']

        await redis_event_manager.unacknowledge(
            target_topic,
            target_group,
            event_ids,
            intent=intent,
        )

        mock_redis_client.xnack.assert_called_once_with(
            target_topic, target_group, expected_mode, '171000000-0', '171000000-1'
        )

    async def test_unacknowledge_does_nothing_when_ids_empty(
        self, redis_event_manager: RedisStreamManager, mock_redis_client: AsyncMock
    ) -> None:
        """Tests calling unacknowledge bypasses xnack if the provided list is empty."""
        await redis_event_manager.unacknowledge(
            'events:telemetry:raw', 'group:timescale_storage', []
        )

        mock_redis_client.xnack.assert_not_called()
