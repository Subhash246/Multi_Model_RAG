"""
MinIO implementation of the storage provider.

This is the only module that knows that MinIO is being used.
"""

from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings
from app.services.storage.base import BaseStorageProvider


settings = get_settings()


class MinIOStorage(BaseStorageProvider):

    def __init__(self) -> None:

        self._client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )

        self._bucket = settings.minio_bucket

    def upload(
        self,
        file_object: BinaryIO,
        object_key: str,
        content_type: str,
        size: int,
    ) -> None:

        self._client.put_object(
            bucket_name=self._bucket,
            object_name=object_key,
            data=file_object,
            length=size,
            content_type=content_type,
        )

    def download(
        self,
        object_key: str,
    ) -> bytes:

        response = self._client.get_object(
            self._bucket,
            object_key,
        )

        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def delete(
        self,
        object_key: str,
    ) -> None:

        self._client.remove_object(
            self._bucket,
            object_key,
        )

    def exists(
        self,
        object_key: str,
    ) -> bool:

        try:
            self._client.stat_object(
                self._bucket,
                object_key,
            )

            return True

        except S3Error as exc:

            if exc.code in {
                "NoSuchKey",
                "NoSuchObject",
                "NotFound",
            }:
                return False

            raise


storage = MinIOStorage()