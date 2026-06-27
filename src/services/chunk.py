import logging

from repositories.chunk import ChunkRepository
from services.consumer import ConsumerBase
from services.splitter import TokenTextSplitter
from services.storage import MinioStorage

logger = logging.getLogger("Consumer")


class Chunker:
    def __init__(
        self,
        repository: ChunkRepository,
        splitter: TokenTextSplitter,
        consumer: ConsumerBase,
        storage: MinioStorage,
    ):
        self.reposiotry = repository
        self.splitter = splitter
        self.consumer = consumer
        self.storage = storage

    async def save_schunks(self):
        logger.info("Сохранение чанков докумнета")
        async for message in self.consumer.read_messages():
            logger.info(
                f"Успешно перехвачено сообщение из Kafka! Офсет: {message.offset}"  # noqa: E501
            )

            raw_data = message.value
            logger.info(f"{raw_data}")
