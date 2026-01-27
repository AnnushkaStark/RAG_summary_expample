from sqlalchemy import delete
from sqlalchemy import exists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Document

from .base import RepositoryBase


class DocumentRepository(RepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Document)

    async def get_file_hash_exists(self, file_hash: str) -> bool:
        result = await self.session.execute(
            select(exists().where(self.model.doc_hash == file_hash))
        )
        return result.scalar()

    async def remove_doc_by_ulr(self, doc_url: str) -> None:
        await self.session.execute(
            delete(self.model).where(self.model.doc_url == doc_url)
        )
        await self.session.commit()
