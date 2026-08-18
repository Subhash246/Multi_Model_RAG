from abc import ABC, abstractmethod
from collections.abc import BinaryIO


class BaseObjectStorage(ABC):

    @abstractmethod
    def upload(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: str,
        size: int,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, object_name: str) -> None:
        raise NotImplementedError