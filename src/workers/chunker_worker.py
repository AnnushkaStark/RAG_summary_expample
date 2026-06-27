import asyncio

from databases.database import get_async_session
from repositories.chunk import ChunkRepository
from services.chunk import Chunker
from services.consumer import ConsumerBase
from services.splitter import TokenTextSplitter
from services.storage import MinioStorage


async def get_documents_chunks() -> None:
    async for session in get_async_session():
        chunk_repo = ChunkRepository(session=session)
        storage = MinioStorage()
        splitter = TokenTextSplitter()
        consumer = ConsumerBase(topic="chunk_topic")
        chunker = Chunker(
            repository=chunk_repo,
            splitter=splitter,
            consumer=consumer,
            storage=storage,
        )
        await chunker.save_schunks()


if __name__ == "__main__":
    asyncio.run(get_documents_chunks())
