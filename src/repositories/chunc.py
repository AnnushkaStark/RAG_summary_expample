from sqlalchemy.ext.asyncio import AsyncSession

from models import Chunk

from .base import RepositoryBase


class ChunkRepository(RepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Chunk)
