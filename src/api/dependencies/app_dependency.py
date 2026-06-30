from typing import Annotated

from fastapi import Depends

from api.dependencies.database import Session
from repositories.document import DocumentRepository
from services.document import DocumentService
from services.storage import MinioStorage


def get_storage() -> MinioStorage:
    return MinioStorage()


StorageDepends = Annotated[MinioStorage, Depends(get_storage)]


def get_document_repo(
    session: Session,
) -> DocumentRepository:
    return DocumentRepository(session=session)


DocumentRepositoryDepends = Annotated[
    DocumentRepository, Depends(get_document_repo)
]


def get_document_service(
    repository: DocumentRepositoryDepends,
    storage: StorageDepends,
) -> DocumentService:
    return DocumentService(
        repository=repository,
        storage=storage,
    )


DocumentServiceDepends = Annotated[
    DocumentService, Depends(get_document_service)
]
