"""
Storage provider abstraction.

The rest of the application depends on this interface,
not on MinIO directly.

This allows the underlying object-storage implementation
to be replaced later without changing API endpoints or
ingestion services.
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseStorageProvider(ABC):

    @abstractmethod
    def upload(
        self,
        file_object: BinaryIO,
        object_key: str,
        content_type: str,
        size: int,
    ) -> None:
        """
        Upload a file to object storage.
        """
        raise NotImplementedError

    @abstractmethod
    def download(
        self,
        object_key: str,
    ) -> bytes:
        """
        Download an object from storage.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        object_key: str,
    ) -> None:
        """
        Delete an object from storage.
        """
        raise NotImplementedError

    @abstractmethod
    def exists(
        self,
        object_key: str,
    ) -> bool:
        """
        Check whether an object exists.
        """
        raise NotImplementedError