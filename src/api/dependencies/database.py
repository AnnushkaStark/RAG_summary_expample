from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from databases.database import async_session


async def get_async_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_async_db)]
