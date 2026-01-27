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
