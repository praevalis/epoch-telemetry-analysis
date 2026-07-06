from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.dependencies.machine import get_machine_service
from api.schemas.pagination import PaginationResponse
from engine.application.machine_service import MachineService
from engine.domain.machine import (
    MachineCreate,
    MachineFilterParams,
    MachineResponse,
    MachineUpdate,
)

router = APIRouter(prefix='/machines', tags=['Machines'])


@router.post('', response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(
    payload: MachineCreate,
    machine_service: Annotated[MachineService, Depends(get_machine_service)],
):
    """Creates a new machine."""
    return await machine_service.create_machine(payload)


@router.get('', response_model=PaginationResponse[MachineResponse])
async def get_many_machines(
    filter_params: Annotated[MachineFilterParams, Depends()],
    machine_service: Annotated[MachineService, Depends(get_machine_service)],
):
    """Retrieves a paginated list of machines."""
    machines, total = await machine_service.get_many_machines(filter_params)

    return PaginationResponse(
        items=machines,
        total=total,
        limit=filter_params.limit,
        offset=filter_params.offset,
    )


@router.get('/{machine_id}', response_model=MachineResponse)
async def get_machine(
    machine_id: UUID,
    machine_service: Annotated[MachineService, Depends(get_machine_service)],
):
    """Retrieves a specific machine by its ID."""
    return await machine_service.get_machine_by_id(machine_id)


@router.patch('/{machine_id}', response_model=MachineResponse)
async def update_machine(
    machine_id: UUID,
    payload: MachineUpdate,
    machine_service: Annotated[MachineService, Depends(get_machine_service)],
):
    """Updates an existing machine.

    Uses PATCH to support partial updates as defined by MachineUpdate schema.
    """
    return await machine_service.update_machine(machine_id, payload)


@router.delete('/{machine_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(
    machine_id: UUID,
    machine_service: Annotated[MachineService, Depends(get_machine_service)],
):
    """Deletes a machine."""
    await machine_service.delete_machine(machine_id)
