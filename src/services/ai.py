from typing import Literal

from openai import AsyncClient

from config.configs import openai_settings
from schemas import CreateSummary
from schemas import RawSummary
from utils.logger import logger
from utils.promt import get_chunk_prompt
from utils.promt import get_final_promt
import re


class OpenAiClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.system_message = (
            "Ты — профессиональный редактор и аналитик текстов"
        )
        self.client = None

    def _init_client(self):
        if not self.client:
            self.client = AsyncClient(
                api_key=openai_settings.API_KEY, base_url=self.base_url
            )

    def _get_promt(self, text: str, mode: Literal["full", "chunk"]) -> str:
        logger.info("Создание промта")
        return (
            get_final_promt(text=text)
            if mode == "full"
            else get_chunk_prompt(text=text)
        )

    async def _get_raw_summary(self, prompt: str) -> RawSummary:
        self._init_client()
        logger.info("Саммаризация текста")
        try:
            response = await self.client.beta.chat.completions.create(
                model="openai/gpt-4o",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
            )  # в идеале нужен профи аккаунт чтоб мог жрать больше токенов
            logger.info(f"{response}")
            return response.to_json()
        except Exception as e:
            logger.error(f"Ошибка  саммаризации: {e}")
            return

    async def _get_embedding(self, text: str) -> list[float]:
        self._init_client()
        logger.info("Получение эмбеддинга")
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=[text],  # эта тварь не возвращет статус кода
                dimensions=384,  # только если через httpx делать
            )  # поэтому только жесть только хардкор только трай эксепт
            # я в курсе что это всрато дорогая конструкция и бла бла бла
            return response.model_dump()["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Ошибка генерации вектора: {e}")
            return

    async def get_summary(
        self, text: str, mode: Literal["full", "chunk"]
    ) -> CreateSummary:
        summary = await self._get_raw_summary(
            prompt=self._get_promt(text=text, mode=mode)
        )
        embedding = await self._get_embedding(text=text)
        if summary and embedding:
            cleaned_summary = summary.replace("\n", " ").replace("\t", " ").replace('\\"', '"')
        
        cleaned_summary = re.sub(r'\s+', ' ', cleaned_summary)
        
        cleaned_summary = cleaned_summary.strip()
            
        return CreateSummary(
                summary_text=cleaned_summary, summary_embedding=embedding
            )
