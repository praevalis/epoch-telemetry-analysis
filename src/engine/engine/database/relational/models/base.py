from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model from which other ORM models inherit. Stores
    metadata for all models."""
