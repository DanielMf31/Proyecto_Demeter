from abc import ABC, abstractmethod
from typing import Any

class TransportProtocol(ABC):
    """
    Interfaz base para protocolos de comunicación (UART, TCP, etc).
    Solo se incluye si cookiecutter.include_protocols == 'yes'.
    """

    @abstractmethod
    def connect(self) -> bool:
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def send(self, data: bytes) -> bool:
        pass

    @abstractmethod
    def receive(self, size: int) -> bytes:
        pass
