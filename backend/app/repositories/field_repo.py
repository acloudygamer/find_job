from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import FieldDB
from app.api.schemas import FieldCreate, FieldUpdate


class FieldRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_module(self, module_id: str) -> List[FieldDB]:
        result = await self.session.execute(
            select(FieldDB)
            .where(FieldDB.module_id == module_id)
            .order_by(FieldDB.order_index)
        )
        return list(result.scalars().all())

    async def get_by_id(self, field_id: str) -> Optional[FieldDB]:
        result = await self.session.execute(
            select(FieldDB).where(FieldDB.id == field_id)
        )
        return result.scalar_one_or_none()

    async def create(self, module_id: str, data: FieldCreate) -> FieldDB:
        field = FieldDB(
            module_id=module_id,
            key=data.key,
            value=data.value,
            field_type=data.field_type,
            order_index=str(data.order_index),
        )
        self.session.add(field)
        await self.session.flush()
        await self.session.refresh(field)
        return field

    async def update(self, field: FieldDB, data: FieldUpdate) -> FieldDB:
        if data.key is not None:
            field.key = data.key
        if data.value is not None:
            field.value = data.value
        if data.field_type is not None:
            field.field_type = data.field_type
        if data.order_index is not None:
            field.order_index = str(data.order_index)
        await self.session.flush()
        await self.session.refresh(field)
        return field

    async def delete(self, field: FieldDB) -> None:
        await self.session.delete(field)
        await self.session.flush()

    async def reorder(self, items: List[dict]) -> None:
        for item in items:
            result = await self.session.execute(
                select(FieldDB).where(FieldDB.id == item["id"])
            )
            f = result.scalar_one_or_none()
            if f:
                f.order_index = str(item["order_index"])
        await self.session.flush()
