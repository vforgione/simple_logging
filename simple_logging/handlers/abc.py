# pylint: disable=C0115,C0116

from abc import ABC, abstractmethod


class Handler(ABC):
    @abstractmethod
    def write(self, message: str) -> None:
        raise NotImplementedError
