import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from io import BytesIO
from typing import Literal

from aioboto3 import Session
from aiobotocore.client import AioBaseClient
from fastapi import UploadFile

from config.configs import minio_settings
from utils.errors.api_errors import DomainError
from utils.errors.api_errors import ErrorCodes
from utils.logger import logger


class MinioStorage:
    def __init__(self):
        self.session = Session(
            aws_access_key_id=minio_settings.MINIO_ROOT_USER,
            aws_secret_access_key=minio_settings.MINIO_ROOT_PASSWORD,
        )
        self.bucket = "files"
        self.folders = "files"

    async def _init_storage(self) -> None:
        logger.info(f"Инициализация хранилища. Проверка бакета: {self.bucket}")
        async with self._get_client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket)
                logger.info(
                    f"Бакет '{self.bucket}' уже существует и готов к работе."
                )
            except Exception:
                logger.warning(
                    f"Бакет '{self.bucket}' не найден. Запуск создания..."
                )
                await client.create_bucket(Bucket=self.bucket)

    @asynccontextmanager
    async def _get_client(self) -> AsyncIterator[AioBaseClient]:
        async with self.session.client(
            service_name="s3",
            endpoint_url=minio_settings.MINIO_ENDPOINT,
            use_ssl=True,
        ) as client:
            yield client

    def _get_secure_name(
        self, file: UploadFile, folder: Literal["files"]
    ) -> str:
        logger.info("Создание защищенного имени файла")
        file_extend = file.filename.split(".")[-1]
        return f"{folder}/{str(uuid.uuid4())}.{file_extend}"

    async def upload_file(
        self,
        folder: Literal["files"],
        file: UploadFile,
    ) -> str:
        await self._init_storage()
        async with self._get_client() as client:
            secure_name = self._get_secure_name(file=file, folder=folder)
            logger.info("Сохранение файла")
            file_data = await file.read()
            try:
                await client.put_object(
                    Bucket=self.bucket,
                    Key=secure_name,
                    ContentLength=file.size,
                    ContentType=file.content_type,
                    Body=file_data,
                )

            except Exception as err:
                logger.error(f"Ошибка сохранения файла {err}")
                raise DomainError(ErrorCodes.ERROR_SAVE_FILE) from err
            logger.info("Файл успешно сохранен")
            return f"{minio_settings.MINIO_SERVER_URL}/{self.bucket}/{secure_name}"  # noqa: E501

    async def remove_file(self, file_url: str) -> str:
        logger.info("Удаление файла")
        async with self._get_client() as client:
            file_url = file_url.split("/")
            try:
                await client.delete_object(
                    Bucket=self.bucket, Key=file_url[-1]
                )
            except Exception as err:
                logger.error(f"Ошибка удадения файла {err}")
                raise DomainError(ErrorCodes.ERROR_REMOVE_FILE) from err
            logger.info("Файл удален")
            return "Ok"

    async def get_file(self, file_url: str) -> BytesIO:
        logger.info("Получение асинхронного потока файла из MinIO")
        url_parts = file_url.split("/")
        object_key = "/".join(url_parts[4:])

        async with self._get_client() as client:
            response = await client.get_object(
                Bucket=url_parts[-2], Key=object_key
            )

            file_bytes = BytesIO()

            async for chunk in response["Body"].content.iter_chunked(
                1024 * 64
            ):
                actual_chunk = chunk[0] if isinstance(chunk, tuple) else chunk
                file_bytes.write(actual_chunk)

            file_bytes.seek(0)
            return file_bytes
