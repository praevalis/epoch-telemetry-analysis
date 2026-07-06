from engine.domain.common import BaseDomainModel


class PaginationResponse[T](BaseDomainModel):
    """Generic envelope for paginated API response."""

    items: list[T]
    total: int
    limit: int
    offset: int
