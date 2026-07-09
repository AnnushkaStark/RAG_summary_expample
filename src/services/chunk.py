import json
from datetime import datetime

from constants.doc_status import DocumentStatus
from repositories.chunk import ChunkRepository
from repositories.document import DocumentRepository
from schemas.chunk import ChunkBase
from schemas.document import DocumentUpdate
from schemas.events import MakeSummarizeChunks
from services.consumer import ConsumerBase
from services.producer import producer
from services.splitter import TokenTextSplitter
from services.storage import MinioStorage
from services.text_extractor import PDFTextExtractor
from utils.logger import logger


class Chunker:
    def __init__(
        self,
        repository: ChunkRepository,
        splitter: TokenTextSplitter,
        consumer: ConsumerBase,
        storage: MinioStorage,
        text_extrator: PDFTextExtractor,
        document_repository: DocumentRepository,
    ):
        self.reposiotry = repository
        self.splitter = splitter
        self.consumer = consumer
        self.storage = storage
        self.text_extrator = text_extrator
        self.document_respository = document_repository

    async def save_schunks(self):
        logger.info("Сохранение чанков докумнета")
        async for message in self.consumer.read_messages():
            logger.info(
                f"Успешно перехвачено сообщение из Kafka! Офсет: {message.offset}"  # noqa: E501
            )

            raw_data = json.loads(message.value)
            file_id = raw_data["file_id"]
            file_bytes = await self.storage.get_file(
                file_url=raw_data["file_url"]
            )
            text = self.text_extrator.extract_text_from_bytes(
                bytes_sretam=file_bytes
            )
            logger.info(f"{text}")
            chunks = self.splitter.split_text(text=text)
            logger.info(f"{chunks}")
            logger.info("Сохранение чанков документа")
            await self.reposiotry.create_bulk(
                schemas=self._get_chunks_schemas(
                    chunks=chunks, doc_id=file_id
                ),
                commit=False,
            )
            logger.info("Обновлние статуса документа")
            await self.document_respository.update(
                schema=DocumentUpdate(
                    status=DocumentStatus.CHUNKED, updated_at=datetime.now()
                ),
                commit=False,
                obj_id=file_id,
            )
            await self.document_respository.session.commit()
            logger.info("Отпрвка события саммаризация чанков")
            await producer.send_message(
                message=MakeSummarizeChunks(file_id=file_id),
                topic=producer.summarize_topic,
            )

    def _get_chunks_schemas(
        self, chunks: list[str], doc_id: int
    ) -> list[ChunkBase]:
        logger.info("Создание схемы чанков")
        return [
            ChunkBase(document_id=doc_id, text=chunk, number=idx)
            for idx, chunk in enumerate(chunks)
        ]
