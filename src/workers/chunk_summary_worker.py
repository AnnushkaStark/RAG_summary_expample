import asyncio

from databases.database import get_async_session
from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from services.consumer import ConsumerBase
from services.summarizer import SummarizerService


async def get_chunks_summary() -> None:
    async for session in get_async_session():
        chunk_repo = ChunkRepository(session=session)
        document_repo = DocumentRepository(session=session)
        consumer = ConsumerBase(topic="summarize_topic")
        service = SummarizerService(
            document_repository=document_repo,
            chunk_repository=chunk_repo,
            consumer=consumer,
        )
        await service.get_chunks_summarize()


if __name__ == "__main__":
    asyncio.run(get_chunks_summary())
