import logging

from aiokafka import AIOKafkaConsumer

from config.configs import kafka_settings

logger = logging.getLogger("Consumer")


class ConsumerBase:
    def __init__(self, topic: str):
        self.topic = topic
        self.consumer = None

    async def _consumer_init(self) -> None:
        if not self.consumer:
            logger.info("Запуск консьюмера")
            self.consumer = AIOKafkaConsumer(
                self.topic,
                bootstrap_servers=kafka_settings.BOOTSTRAP_URL,
                group_id="1",
                auto_offset_reset="earliest",
            )
            await self.consumer.start()
            logger.info("Консьюмер запущен")

    async def read_messages(self):
        await self._consumer_init()
        logger.info(f"Получение сообщения из топика {self.topic}")
        async for message in self.consumer:
            yield message

        if self.consumer:
            logger.info("Закрытие консьюмера")
            await self.consumer.stop()
