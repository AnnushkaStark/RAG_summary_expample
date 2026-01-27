import hashlib
import logging
from typing import Annotated

from fastapi import File
from fastapi import UploadFile

from config.configs import file_settings
from models import Document
from repositories.document import DocumentRepository
from schemas.document import DocumentBase
from schemas.events import MakeChunk
from services.producer import ProducerService
from services.storage import MinioStorage
from utils.errors.api_errors import DomainError
from utils.errors.api_errors import ErrorText

logger = logging.getLogger("DocumentService")


class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        storage: MinioStorage,
        producer: ProducerService,
    ):
        self.repository = repository
        self.storage = storage
        self.producer = producer

    def _get_file_hash(self, file: Annotated[UploadFile, File()]) -> str:
        logger.info("Генерация уникального хэша содержимого файла")
        hash = hashlib.sha256(file.read()).hexdigest()
        file.seek(0)
        return hash

    async def _validate(self, file: Annotated[UploadFile, File()]) -> None:
        logger.info("Валидация файла")
        if file.size == 0:
            logger.warning("Получент пустой файл")
            raise DomainError(ErrorText.FILE_IS_EMPTY)

        if file.size > file_settings.MAX_SIZE:
            logger.warning("Превышен максимальный размер файла")
            raise DomainError(ErrorText.MAXIMUM_FILE_SIZE_EXCEEDED)

        file_hash = self._get_file_hash(file)
        if await self.repository.get_file_hash_exists(file_hash=file_hash):
            logger.warning("Файл уже обрабатывался")
            raise DomainError(ErrorText.FILE_ALREDY_EXSISTS)
        logger.info("Валидация файла успешна")
        return file_hash

    async def create(self, file: Annotated[UploadFile, File()]) -> Document:
        logger.info("Сохранение докумнета")
        file_hash = await self._validate(file=file)
        document = await self.repository.create(
            schema=DocumentBase(
                filename=file.filename,
                doc_url=await self.storage.upload_file(
                    bucket="documents", file=file
                ),
                doc_hash=file_hash,
            )
        )
        await self.producer.send_message(
            message=MakeChunk(file_id=document.id, file_url=document.doc_url),
            topic=self.producer.chunk_topic,
        )
        logger.info("Документ сохранен")
        return document.doc_url

    async def remove(self, doc_url: str) -> None:
        await self.repository.remove_doc_by_ulr(doc_url=doc_url)
        await self.storage.remove_file(file_url=doc_url)
