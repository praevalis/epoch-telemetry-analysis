from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from engine.database.relational.interfaces import ISessionManager

# NOTE: Type alias exported for downstream packages to prevent SQLAlchemy dependency
# May or may not be used inside the `engine` package itself.
DbSession = AsyncSession


class TimescaleSessionManager(ISessionManager):
    """Provides ephemeral, safe context for asynchronous timescaledb operations. It is decoupled
    from heavy TCP connection pools. Should be injected per-request or per-task."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        """Initializes the session manager.

        Args:
            session_factory: A pre-configured SQLAlchemy async_sessionmaker.
        """
        self._session_factory = session_factory

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Async context manager that yields a secure database session.

        Yields:
            AsyncSession: An active SQLAlchemy async session.

        Raises:
            Exception: Re-raises any exceptions caught during execution, after rollback.
        """
        async_session = self._session_factory()

        try:
            yield async_session

            # NOTE: This manager does not call `await session.commit()`. This is an explicit design choice
            # considering the DDD boundaries of the project. Each repository is in-charge of it's own commits.

        except Exception:
            await async_session.rollback()
            raise

        finally:
            await async_session.close()
