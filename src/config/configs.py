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


class FileSettings(BaseSetting):
    MAX_SIZE: int = 10 * 1024 * 1024


class KafkaSettings(BaseSetting):
    BOOTSTRAP_URL: str = "kafka:29092"


kafka_settings = KafkaSettings()
db_settings = DBSettings()
minio_settings = MinioSettings()
file_settings = FileSettings()
