import json

from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from services.consumer import ConsumerBase
from utils.logger import logger


class SummarizerService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        consumer: ConsumerBase,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.consumer = consumer

    async def get_chunks_summarize(self) -> None:
        logger.info("Саммариазция чанков документов")
        async for message in self.consumer.read_messages():
            logger.info(
                f"Успешно перехвачено сообщение из Kafka! Офсет: {message.offset}"  # noqa: E501
            )

            raw_data = json.loads(message.value)
            file_id = raw_data["file_id"]
            logger.info(file_id)
            chunks = await self.chunk_repository.get_by_document_id(
                doc_id=file_id
            )
            logger.info(f"Получено {len(chunks)}")
