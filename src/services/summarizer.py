import json
from datetime import datetime

from constants.doc_status import DocumentStatus
from models import Chunk
from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from schemas.document import DocumentUpdate
from schemas.events import MakeSummarizeAll
from services.ai import OpenAiClient
from services.consumer import ConsumerBase
from services.producer import producer
from utils.logger import logger


class SummarizerService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        chunk_repository: ChunkRepository,
        consumer: ConsumerBase,
        client: OpenAiClient,
    ):
        self.document_repository = document_repository
        self.chunk_repository = chunk_repository
        self.consumer = consumer
        self.client = client

    async def _update_chunks(self, chunks: list[Chunk], file_id: int) -> bool:
        logger.info("Сохраннеие эмбеддингов и сaммаризации чанков")
        counter = 0
        for chunk in chunks:
            update_schema = await self.client.get_summary(
                text=chunk.text, mode="chunk"
            )
            if update_schema:
                logger.info(f"{update_schema}")
                await self.chunk_repository.update(
                    schema=update_schema, obj_id=chunk.id, commit=False
                )
                counter += 1
                logger.info(f"Обработано {counter}")

        logger.info("Обновлние статуса докумнта")
        await self.document_repository.update(
            schema=DocumentUpdate(
                status=DocumentStatus.PROCESSED
                if counter == len(chunks)
                else DocumentStatus.FAILED,
                updated_at=datetime.now(),
            ),
            commit=False,
            obj_id=file_id,
        )
        await self.document_repository.session.commit()
        result = counter == len(chunks)
        logger.info(f"Результат {result}")
        return result

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

            if await self._update_chunks(chunks=chunks, file_id=file_id):
                logger.info("Отправка события саммаризация всего файла")
                await producer.send_message(
                    message=MakeSummarizeAll(file_id=file_id),
                    topic=producer.full_summarize_topic,
                )

            else:
                logger.error("Ошибка саммаризации")
