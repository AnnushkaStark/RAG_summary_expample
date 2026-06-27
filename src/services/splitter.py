import logging

import tiktoken

from utils.errors.other_errors import ChunkerError

logger = logging.getLogger("TextSplitter")


class TokenTextSplitter:
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
        encoding_name: str = "cl100k_base",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding(encoding_name)

        if self.chunk_overlap >= self.chunk_size:
            raise ChunkerError("CHUNK_OVERLAP_EXCEEDS_CHUNK_SIZE")

    def split_text(self, text: str) -> list[str]:
        if not text or not text.strip():
            logger.warning("Передан пустой текст для нарезки чанков")
            return []

        logger.info("Запуск токенизированного разбиения текста документа")

        tokens = self.tokenizer.encode(text)
        total_tokens = len(tokens)
        logger.info(
            f"Документ успешно токенизирован. Всего токенов в ОЗУ воркера: {total_tokens}"  # noqa E501
        )

        chunks = []
        start = 0

        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start:end]

            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text.strip())

            start += self.chunk_size - self.chunk_overlap

        logger.info(
            f"Пайплайн чанкинга завершен. Сгенерировано {len(chunks)} чанков со стейтом SUCCESS"  # noqa: E501
        )
        return chunks
