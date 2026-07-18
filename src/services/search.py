import hashlib
import json

from repositories.document import DocumentRepository
from schemas.document import DocumentResponse
from schemas.pagination import PaginationResponse
from services.ai import OpenAiClient
from services.state import State
from utils.errors.api_errors import DomainError
from utils.errors.api_errors import ErrorCodes
from utils.logger import logger


class SearchService:
    def __init__(
        self,
        repository: DocumentRepository,
        state: State,
        client: OpenAiClient,
    ):
        self.repository = repository
        self.state = state
        self.ai_client = client

    async def _get_embedding_query(self, query: str) -> list[float]:
        logger.info("Получение эмбединга поискового запроса")
        query_hash = hashlib.sha256(query.strip().encode("utf-8")).hexdigest()
        if found_embedding := await self.state.get_state(key=query_hash):
            return json.loads(found_embedding)

        embedding = await self.ai_client._get_embedding(text=query)
        if not embedding:
            raise DomainError(ErrorCodes.ERROR_EMBEDDING_GENERATION)

        await self.state.set_state(
            key=query_hash, value=json.dumps(embedding), ttl=86400
        )
        return embedding

    async def search(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> PaginationResponse[DocumentResponse]:
        search_embedding = await self._get_embedding_query(query=query)
        return await self.repository.search(
            embedding=search_embedding, query=query, limit=limit, offset=offset
        )
