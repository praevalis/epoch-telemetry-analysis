class DomainException(Exception):
    """Base class for all domain and business logic errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
