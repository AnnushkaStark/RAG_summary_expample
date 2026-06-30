import asyncio

from databases.database import get_async_session
from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from services.chunk import Chunker
from services.consumer import ConsumerBase
from services.splitter import TokenTextSplitter
from services.storage import MinioStorage
from services.text_extractor import PDFTextExtractor


async def get_documents_chunks() -> None:
    async for session in get_async_session():
        extrator = PDFTextExtractor()
        chunk_repo = ChunkRepository(session=session)
        document_repo = DocumentRepository(session=session)
        storage = MinioStorage()
        splitter = TokenTextSplitter()
        consumer = ConsumerBase(topic="chunk_topic")
        chunker = Chunker(
            repository=chunk_repo,
            splitter=splitter,
            consumer=consumer,
            storage=storage,
            text_extrator=extrator,
            document_repository=document_repo,
        )
        await chunker.save_schunks()


if __name__ == "__main__":
    asyncio.run(get_documents_chunks())
