from collections.abc import BinaryIO

from minio import Minio

from app.core.config import get_settings
from app.services.storage.base import BaseObjectStorage


settings = get_settings()


class MinIOStorage(BaseObjectStorage):

    def __init__(self) -> None:
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        self.bucket = settings.minio_bucket

        self._ensure_bucket()

    def _ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        size: int,
    ) -> None:

        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_name,
            data=file_data,
            length=size,
            content_type=content_type,
        )

    def delete(self, object_name: str) -> None:
        self.client.remove_object(
            self.bucket,
            object_name,
        )


storage = MinIOStorage()