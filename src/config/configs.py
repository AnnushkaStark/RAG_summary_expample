from pathlib import Path

from .base import BaseSetting

BASE_DIR = Path(__file__).parent.parent


class DBSettings(BaseSetting):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str


class MinioSettings(BaseSetting):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_SECURE: bool
    MINIO_ENDPOINT: str
    MINIO_SERVER_URL: str


db_settings = DBSettings()
minio_settings = MinioSettings()
