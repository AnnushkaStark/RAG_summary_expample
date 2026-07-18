from typing import Annotated

from fastapi import Depends

from api.dependencies.database import Session
from repositories.document import DocumentRepository
from services.ai import OpenAiClient
from services.document import DocumentService
from services.search import SearchService
from services.state import State
from services.storage import MinioStorage


def get_ai_client() -> OpenAiClient:
    return OpenAiClient()


AiClientDepends = Annotated[OpenAiClient, Depends(get_ai_client)]


def get_state() -> State:
    return State()


StateDepends = Annotated[State, Depends(get_state)]


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


def get_seacrch_service(
    repository: DocumentRepositoryDepends,
    state: StateDepends,
    client: AiClientDepends,
) -> SearchService:
    return SearchService(repository=repository, state=state, client=client)


SearchServiceDepends = Annotated[SearchService, Depends(get_seacrch_service)]
