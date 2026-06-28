from typing import Any

from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from databases.database import Base


class RepositoryBase:
    def __init__(self, session: AsyncSession, model: Base):
        self.session = session
        self.model = model

    async def create(self, schema: BaseModel, commit: bool = True) -> Base:
        result = await self.session.execute(
            insert(self.model)
            .values(schema.model_dump())
            .returning(self.model)
        )
        if commit:
            await self.session.commit()
        return result.scalar()

    async def get_by_id(self, obj_id) -> Base:
        return await self.session.get(Base, obj_id)

    async def create_bulk(
        self, schemas: list[BaseModel], commit: bool = True
    ) -> list[Base]:
        data = [s.model_dump() for s in schemas]
        objs = await self.session.execute(
            insert(self.model).values(data).returning(self.model)
        )
        if commit:
            await self.session.commit()
        return objs.scalars().all()

    async def partitial_update(
        self, obj_id: int, new_value: Any, value_name: str, commit: bool = True
    ) -> None:
        obj = await self.get_by_id(obj_id=obj_id)
        if obj:
            obj.__setattr__(value_name, new_value)

        if commit:
            await self.session.commit()
