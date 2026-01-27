import json
import logging
import re
import uuid
from typing import Literal

from fastapi import Response
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error

from config.configs import minio_settings
from utils.errors.api_errors import DomainError
from utils.errors.api_errors import ErrorText
from utils.errors.other_errors import StorageError

logger = logging.getLogger("MinioStorage")


class MinioStorage:
    client = Minio(
        endpoint=minio_settings.MINIO_ENDPOINT,
        access_key=minio_settings.MINIO_ROOT_USER,
        secret_key=minio_settings.MINIO_ROOT_PASSWORD,
        secure=minio_settings.MINIO_SECURE,
    )
    buckets = ["documents"]

    async def _validate_file_name(self, filename: str) -> bool:
        logger.info("Проверка валидности названия файла")
        pattern = re.compile(r"^[^\sа-яА-ЯёЁ]*$")
        return pattern.fullmatch(filename)

    async def _create_buckets(self, bucket: Literal["documents"]) -> None:
        logger.info("Инициализация бакетов")
        for bucket in self.buckets:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                await self._set_public_read(bucket=bucket)

    async def _set_public_read(self, bucket: Literal["documents"]) -> None:
        logger.info("Определение политики доступности бакетов")
        try:
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"],
                    }
                ],
            }

        except S3Error as err:
            logger.error(f"Ошибка политики доступности бакоетов {err}")
            raise DomainError(ErrorText.BUCKET_POLICY_ERROR) from err

        self.client.set_bucket_policy(bucket, json.dumps(policy))

    async def upload_file(
        self,
        bucket: Literal["documents"],
        file: UploadFile,
    ) -> str:
        if not await self._validate_file_name(filename=file.filename):
            logger.warning("Невалидное имя файла")
            raise DomainError(ErrorText.INVALID_FILENAME)

        await self._create_buckets(bucket=bucket)
        logger.info("Загрузка файла в хранилище")
        secure_name = f"{str(uuid.uuid4())}_{file.filename}"

        try:
            self.client.put_object(
                bucket_name=bucket,
                object_name=secure_name,
                length=file.size,
                content_type=file.content_type,
                data=file.file,
            )
        except S3Error as err:
            logger.info(f"Ошибка сохранния файла {err}")
            raise DomainError(ErrorText.ERROR_SAVE_FILE) from err

        return f"{minio_settings.MINIO_SERVER_URL}/{bucket}/{secure_name}"

    async def get_file(self, file_url: str) -> bytes:
        logger.info("Получение файла из s3")
        file_url = file_url.split("/")

        try:
            response = self.client.get_object(
                bucket_name=file_url[-2], object_name=file_url[-1]
            )
        except S3Error as e:
            logger.error(f"Ошибка получение файла {str(e)}")
            raise StorageError(f"Ошибка получение файла {str(e)}") from e

        content_type = response.headers.get(
            "content-type", "application/octet-stream"
        )
        return Response(
            content=response.read(),
            media_type=content_type,
        )

    async def remove_file(self, file_url: str) -> str:
        file_url = file_url.split("/")
        try:
            self.client.remove_object(
                bucket_name=file_url[-2], object_name=file_url[-1]
            )
        except S3Error as err:
            raise DomainError(ErrorText.ERROR_REMOVE_FILE) from err
        return "Ok"
