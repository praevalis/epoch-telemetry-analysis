from typing import Any, Literal, Protocol


class IEventManager(Protocol):
    """Generic contract for event-driven pub/sub operations."""

    async def publish(self, topic: str, payload: dict[str, Any], **kwargs: Any) -> str:
        """Publishes an event payload to a topic.

        Args:
            topic: Topic identifier.
            payload: Event data to be published

        Returns:
            Broker generated, unique event ID.
        """
        ...

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
            topic: Topic to be polled.
            group: Consumer group for which the topic is polled.
            consumer_id: Identifier for the consumer.
            batch_size: Number of unacknowledged events to fetch in the batch.
            timeout_ms: Timeout limit in milliseconds.

        Returns:
            Unacknowledged identifier and event payload pairs.
        """
        ...

    async def acknowledge(self, topic: str, group: str, event_ids: list[str]) -> None:
        """Acknowledges that a batch of events have been processed for the group.

        Args:
            topic: Topic to send the acknowledgement.
            group: Group that processed the events.
            event_ids: Identifiers for events that were processed.
        """
        ...

    async def unacknowledge(
        self,
        topic: str,
        group: str,
        event_ids: list[str],
        intent: Literal['retry', 'discard', 'reset'] = 'retry',
    ) -> None:
        """Relinquishes ownership of events, instructing the broker how to handle recovery.

        Args:
            topic: Topic to re-add the event.
            group: Group that processes the events.
            event_ids: Identifiers for the events to be unacknowledged.
            intent: Recovery mode.
        """
        ...

    async def ensure_group(self, topic: str, group: str) -> None:
        """Idempotently registers a consumer group for a topic.

        Args:
            topic: Topic to register the group.
            group: Group to be registered.
        """
        ...
