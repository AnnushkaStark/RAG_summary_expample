from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.database import get_async_db
from repositories.document import DocumentRepository
from services.document import DocumentService
from services.producer import ProducerService
from services.storage import MinioStorage


def get_storage() -> MinioStorage:
    return MinioStorage()


def get_producer() -> ProducerService:
    return ProducerService()


def get_document_repo(
    session: Annotated[AsyncSession, Depends(get_async_db)],
) -> DocumentRepository:
    return DocumentRepository(session=session)


def get_document_service(
    repository: Annotated[DocumentRepository, Depends(get_document_repo)],
    storage: Annotated[MinioStorage, Depends(get_storage)],
    producer: Annotated[ProducerService, Depends(get_producer)],
) -> DocumentService:
    return DocumentService(
        repository=repository, storage=storage, producer=producer
    )
