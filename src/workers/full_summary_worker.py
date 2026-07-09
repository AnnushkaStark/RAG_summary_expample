import asyncio

from databases.database import get_async_session
from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from services.ai import OpenAiClient
from services.consumer import ConsumerBase
from services.summarizer import SummarizerService


async def get_document_summary() -> None:
    async for session in get_async_session():
        chunk_repo = ChunkRepository(session=session)
        document_repo = DocumentRepository(session=session)
        consumer = ConsumerBase(topic="full_summarize_topic")
        client = OpenAiClient()
        service = SummarizerService(
            document_repository=document_repo,
            chunk_repository=chunk_repo,
            consumer=consumer,
            client=client,
        )
        await service.get_full_summary()


if __name__ == "__main__":
    asyncio.run(get_document_summary())
