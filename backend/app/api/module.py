from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.schemas import (
    ApiResponse,
    ModuleCreate,
    ModuleUpdate,
    ModuleResponse,
    ReorderModulesRequest,
    List,
)
from app.repositories.module_repo import ModuleRepository
from app.repositories.resume_repo import ResumeRepository

router = APIRouter(tags=["modules"])


@router.get(
    "/resumes/{resume_id}/modules", response_model=ApiResponse[List[ModuleResponse]]
)
async def list_modules(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ModuleRepository(db)
    modules = await repo.list_by_resume(resume_id)
    return ApiResponse.ok([ModuleResponse.model_validate(m) for m in modules])


@router.post(
    "/resumes/{resume_id}/modules",
    response_model=ApiResponse[ModuleResponse],
    status_code=201,
)
async def create_module(
    resume_id: str,
    data: ModuleCreate,
    db: AsyncSession = Depends(get_db),
):
    resume_repo = ResumeRepository(db)
    resume = await resume_repo.get_by_id(resume_id)
    if not resume:
        return ApiResponse.fail("Resume not found")
    repo = ModuleRepository(db)
    module = await repo.create(resume_id, data)
    return ApiResponse.ok(ModuleResponse.model_validate(module))


@router.get("/modules/{module_id}", response_model=ApiResponse[ModuleResponse])
async def get_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ModuleRepository(db)
    module = await repo.get_by_id(module_id)
    if not module:
        return ApiResponse.fail("Module not found")
    return ApiResponse.ok(ModuleResponse.model_validate(module))


@router.put("/modules/{module_id}", response_model=ApiResponse[ModuleResponse])
async def update_module(
    module_id: str,
    data: ModuleUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ModuleRepository(db)
    module = await repo.get_by_id(module_id)
    if not module:
        return ApiResponse.fail("Module not found")
    updated = await repo.update(module, data)
    return ApiResponse.ok(ModuleResponse.model_validate(updated))


@router.delete("/modules/{module_id}", response_model=ApiResponse)
async def delete_module(
    module_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ModuleRepository(db)
    module = await repo.get_by_id(module_id)
    if not module:
        return ApiResponse.fail("Module not found")
    await repo.delete(module)
    return ApiResponse.ok(None)


@router.patch("/modules/reorder", response_model=ApiResponse)
async def reorder_modules(
    data: ReorderModulesRequest,
    db: AsyncSession = Depends(get_db),
):
    repo = ModuleRepository(db)
    await repo.reorder(
        [{"id": item.id, "order_index": item.order_index} for item in data.items]
    )
    return ApiResponse.ok(None)
