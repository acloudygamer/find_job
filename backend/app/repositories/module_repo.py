from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import ModuleDB
from app.api.schemas import ModuleCreate, ModuleUpdate


class ModuleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_resume(self, resume_id: str) -> List[ModuleDB]:
        result = await self.session.execute(
            select(ModuleDB)
            .where(ModuleDB.resume_id == resume_id)
            .order_by(ModuleDB.order_index)
        )
        return list(result.scalars().all())

    async def get_by_id(self, module_id: str) -> Optional[ModuleDB]:
        result = await self.session.execute(
            select(ModuleDB).where(ModuleDB.id == module_id)
        )
        return result.scalar_one_or_none()

    async def create(self, resume_id: str, data: ModuleCreate) -> ModuleDB:
        module = ModuleDB(
            resume_id=resume_id,
            module_type=data.module_type,
            title=data.title,
            content=data.content or {},
            order_index=str(data.order_index),
        )
        self.session.add(module)
        await self.session.flush()
        await self.session.refresh(module)
        return module

    async def update(self, module: ModuleDB, data: ModuleUpdate) -> ModuleDB:
        if data.module_type is not None:
            module.module_type = data.module_type
        if data.title is not None:
            module.title = data.title
        if data.content is not None:
            module.content = data.content
        if data.order_index is not None:
            module.order_index = str(data.order_index)
        await self.session.flush()
        await self.session.refresh(module)
        return module

    async def delete(self, module: ModuleDB) -> None:
        await self.session.delete(module)
        await self.session.flush()

    async def reorder(self, items: List[dict]) -> None:
        for item in items:
            result = await self.session.execute(
                select(ModuleDB).where(ModuleDB.id == item["id"])
            )
            module = result.scalar_one_or_none()
            if module:
                module.order_index = str(item["order_index"])
        await self.session.flush()
