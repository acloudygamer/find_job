from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.schemas import (
    ApiResponse,
    FieldCreate,
    FieldUpdate,
    FieldResponse,
    ReorderFieldsRequest,
    List,
)
from app.repositories.field_repo import FieldRepository
from app.repositories.module_repo import ModuleRepository

router = APIRouter(tags=["fields"])


@router.get(
    "/modules/{module_id}/fields", response_model=ApiResponse[List[FieldResponse]]
)
async def list_fields(
    module_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = FieldRepository(db)
    fields = await repo.list_by_module(module_id)
    return ApiResponse.ok([FieldResponse.model_validate(f) for f in fields])


@router.post(
    "/modules/{module_id}/fields",
    response_model=ApiResponse[FieldResponse],
    status_code=201,
)
async def create_field(
    module_id: str,
    data: FieldCreate,
    db: AsyncSession = Depends(get_db),
):
    module_repo = ModuleRepository(db)
    module = await module_repo.get_by_id(module_id)
    if not module:
        return ApiResponse.fail("Module not found")
    repo = FieldRepository(db)
    field = await repo.create(module_id, data)
    return ApiResponse.ok(FieldResponse.model_validate(field))


@router.put("/fields/{field_id}", response_model=ApiResponse[FieldResponse])
async def update_field(
    field_id: str,
    data: FieldUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = FieldRepository(db)
    field = await repo.get_by_id(field_id)
    if not field:
        return ApiResponse.fail("Field not found")
    updated = await repo.update(field, data)
    return ApiResponse.ok(FieldResponse.model_validate(updated))


@router.delete("/fields/{field_id}", response_model=ApiResponse)
async def delete_field(
    field_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = FieldRepository(db)
    field = await repo.get_by_id(field_id)
    if not field:
        return ApiResponse.fail("Field not found")
    await repo.delete(field)
    return ApiResponse.ok(None)


@router.patch("/fields/reorder", response_model=ApiResponse)
async def reorder_fields(
    data: ReorderFieldsRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = FieldRepository(db)
    await repo.reorder(
        [{"id": item.id, "order_index": item.order_index} for item in data.items]
    )
    return ApiResponse.ok(None)
