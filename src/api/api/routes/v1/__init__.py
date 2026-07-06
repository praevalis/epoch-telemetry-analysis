from fastapi import APIRouter

from .machine import router as machine_router

v1_router = APIRouter(prefix='/api/v1')

v1_router.include_router(machine_router)

__all__ = ['v1_router']
