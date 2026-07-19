from typing import Any, Final, Literal, cast

from redis.asyncio import Redis
from redis.exceptions import ResponseError

from .interfaces import IEventManager

RECOVERY_MODE_MAP: Final[
    dict[Literal['retry', 'discard', 'reset'], Literal['FAIL', 'FATAL', 'SILENT']]
] = {
    'retry': 'FAIL',  # keeps the counter
    'discard': 'FATAL',  # sets the counter to maximum
    'reset': 'SILENT',  # decrements the counter
}


class RedisStreamManager(IEventManager):
    """Concrete Redis stream manager for IEventManager protocol."""

    def __init__(self, client: Redis) -> None:
        """Initializes the stream manager.

        Args:
            client: Pre-configured Redis client.
        """
        self._client = client

    async def publish(self, topic: str, payload: dict[str, Any], **kwargs: Any) -> str:
        """Publishes an event payload to a topic.

        Args:
            topic: Stream identifier.
            payload: Event fields to be published

        Returns:
            Redis generated, unique entry ID.
        """
        maxlen = kwargs.get('maxlen', 100000)
        encodable_fields = cast(
            dict[Any, Any], payload
        )  # Cast to satisfy invariant dict[FieldT, EncodableT]

        msg_id = await self._client.xadd(
            name=topic, fields=encodable_fields, maxlen=maxlen, approximate=True
        )
        return msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)

    async def consume(
        self,
        topic: str,
        group: str,
        consumer_id: str,
        batch_size: int = 1000,
        timeout_ms: int = 200,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Polls the broker for a batch of unacknowledged events for a consumer group.

        Args:
            topic: Stream to be polled.
            group: Consumer group for which the stream is polled.
            consumer_id: Identifier for the consumer.
            batch_size: Number of unacknowledged entries to fetch in the batch.
            timeout_ms: Timeout limit in milliseconds.

        Returns:
            Unacknowledged identifier and payload pairs.
        """
        await self.ensure_group(topic, group)

        messages = await self._client.xreadgroup(
            groupname=group,
            consumername=consumer_id,
            streams={topic: '>'},
            count=batch_size,
            block=timeout_ms,
        )

        if not messages:
            return []

        if isinstance(messages, dict):
            stream_data = messages.get(topic) or messages.get(topic.encode('utf-8'), [])
        else:
            stream_data = messages[0][1]

        if not stream_data:
            return []

        parsed_events: list[tuple[str, dict[str, Any]]] = []

        for entry in stream_data:
            if not isinstance(entry, (tuple, list)) or len(entry) < 2:
                continue

            msg_id, data = entry[0], entry[1]

            if not isinstance(data, dict):
                continue

            payload = cast(dict[str, Any], data)

            msg_id = msg_id.decode('utf-8') if isinstance(msg_id, bytes) else str(msg_id)
            parsed_events.append((msg_id, payload))

        return parsed_events

    async def acknowledge(self, topic: str, group: str, event_ids: list[str]) -> None:
        """Acknowledges that a batch of events have been processed for the group.

        Args:
            topic: Stream to send the acknowledgement.
            group: Group that processed the entries.
            event_ids: Identifiers for stream entries that were processed.
        """
        if event_ids:
            await self._client.xack(topic, group, *event_ids)

    async def unacknowledge(
        self,
        topic: str,
        group: str,
        event_ids: list[str],
        intent: Literal['retry', 'discard', 'reset'] = 'retry',
    ) -> None:
        """Relinquishes ownership of events, instructing the broker how to handle recovery.

        Args:
            topic: Stream to which the entries belong.
            group: Consumer group that processes the entries.
            event_ids: Identifiers for stream entries to be unacknowledged.
            intent: Specifies recovery mode. Mapped to Redis modes.
        """
        if not event_ids:
            return

        recovery_mode = RECOVERY_MODE_MAP[intent]
        await self._client.xnack(topic, group, recovery_mode, *event_ids)

    async def ensure_group(self, topic: str, group: str) -> None:
        """Idempotently registers a consumer group for a topic.

        Args:
            topic: Stream to register the group.
            group: Group to be registered.
        """
        try:
            await self._client.xgroup_create(name=topic, groupname=group, id='0', mkstream=True)
        except ResponseError as e:
            if 'BUSYGROUP' in str(e):
                # Consume group already exists, safe to ignore.
                pass
            else:
                raise
