"""Handles middleware logic and handlers for the application."""

from .cors_middleware import configure_cors

__all__ = ['configure_cors']
