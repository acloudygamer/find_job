from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.schemas import (
    ApiResponse,
    ResumeCreate,
    ResumeUpdate,
    ResumeResponse,
    PaginatedData,
    PaginationMeta,
)
from app.repositories.resume_repo import ResumeRepository

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("", response_model=ApiResponse[PaginatedData[ResumeResponse]])
async def list_resumes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resumes, total = await repo.list(page=page, limit=limit)
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    data = PaginatedData(
        data=[ResumeResponse.model_validate(r) for r in resumes],
        meta=PaginationMeta(
            total=total, page=page, limit=limit, total_pages=total_pages
        ),
    )
    return ApiResponse.ok(data)


@router.post("", response_model=ApiResponse[ResumeResponse], status_code=201)
async def create_resume(
    data: ResumeCreate,
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.create(data)
    return ApiResponse.ok(ResumeResponse.model_validate(resume))


@router.get("/{resume_id}", response_model=ApiResponse[ResumeResponse])
async def get_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(resume_id)
    if not resume:
        return ApiResponse.fail("Resume not found")
    return ApiResponse.ok(ResumeResponse.model_validate(resume))


@router.put("/{resume_id}", response_model=ApiResponse[ResumeResponse])
async def update_resume(
    resume_id: str,
    data: ResumeUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(resume_id)
    if not resume:
        return ApiResponse.fail("Resume not found")
    updated = await repo.update(resume, data)
    return ApiResponse.ok(ResumeResponse.model_validate(updated))


@router.delete("/{resume_id}", response_model=ApiResponse)
async def delete_resume(
    resume_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = ResumeRepository(db)
    resume = await repo.get_by_id(resume_id)
    if not resume:
        return ApiResponse.fail("Resume not found")
    await repo.delete(resume)
    return ApiResponse.ok(None)
