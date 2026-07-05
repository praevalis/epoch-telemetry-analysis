from typing import Protocol


class ITransactionManager(Protocol):
    """Cross-domain boundary for managing transactional state.
    Allows the application layer to finalize or abort operations
    without knowing the underlying database infrastructure.
    """

    async def commit(self) -> None:
        """Persists the transaction."""
        ...

    async def rollback(self) -> None:
        """Aborts the transaction."""
        ...
