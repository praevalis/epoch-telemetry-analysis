from sqlalchemy.ext.asyncio import AsyncSession

from engine.domain.common import ITransactionManager


class SqlAlchemyTransactionManager(ITransactionManager):
    """Concrete implementation of ITransactionManager."""

    def __init__(self, session: AsyncSession) -> None:
        """Initializes concrete transaction manager.

        Args:
            session: Session to manage.
        """
        self.session = session

    async def commit(self) -> None:
        """Persists the transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Aborts the transaction."""
        await self.session.rollback()
