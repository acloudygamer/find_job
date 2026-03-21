from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import ResumeDB
from app.api.schemas import ResumeCreate, ResumeUpdate


class ResumeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, page: int = 1, limit: int = 20) -> tuple[List[ResumeDB], int]:
        offset = (page - 1) * limit
        count_result = await self.session.execute(select(func.count(ResumeDB.id)))
        total = count_result.scalar() or 0
        result = await self.session.execute(
            select(ResumeDB)
            .order_by(ResumeDB.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total

    async def get_by_id(self, resume_id: str) -> Optional[ResumeDB]:
        result = await self.session.execute(
            select(ResumeDB).where(ResumeDB.id == resume_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ResumeCreate) -> ResumeDB:
        resume = ResumeDB(name=data.name, description=data.description)
        self.session.add(resume)
        await self.session.flush()
        await self.session.refresh(resume)
        return resume

    async def update(self, resume: ResumeDB, data: ResumeUpdate) -> ResumeDB:
        if data.name is not None:
            resume.name = data.name
        if data.description is not None:
            resume.description = data.description
        await self.session.flush()
        await self.session.refresh(resume)
        return resume

    async def delete(self, resume: ResumeDB) -> None:
        await self.session.delete(resume)
        await self.session.flush()
