from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Chunk

from .base import RepositoryBase


class ChunkRepository(RepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chunk)

    async def get_by_document_id(self, doc_id: int) -> list[Chunk]:
        result = await self.session.execute(
            select(self.model).where(self.model.document_id == doc_id)
        )
        return result.scalars().all()
