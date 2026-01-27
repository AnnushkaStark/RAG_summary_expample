import json
import logging

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from config.configs import kafka_settings

logger = logging.getLogger("ProducerService")


class ProducerService:
    def __init__(self):
        self.bootstrap_url = kafka_settings.BOOTSTRAP_URL
        self.topic = kafka_settings.TOPIC
        self.producer = None
        self.chunk_topic = "chunk_topic"
        self.summarize_topic = "summarize_topic"

    async def start(self) -> None:
        logger.info("Инициализация продюссера")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_url,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        logger.info("Продюссер запущен")
        await self.producer.start()

    async def stop(self) -> None:
        logger.info("Остановка продюссера")
        if self.producer:
            logger.info("Продюссер остановлен")
            await self.producer.stop()

    async def send_message(self, message: BaseModel, topic: str):
        logger.info(f"Отправка cообщения в топик {topic}")

        if not self.producer:
            await self.start()
        await self.producer.send(topic=topic, value=message.model_dump())
