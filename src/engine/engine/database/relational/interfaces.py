from contextlib import AbstractAsyncContextManager
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession


class ISessionManager(Protocol):
    """Generic contract for relational db session manager."""

    def session(self) -> AbstractAsyncContextManager[AsyncSession]:
        """Returns a context manager for a database session."""
        ...
