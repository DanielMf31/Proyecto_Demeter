from abc import ABC, abstractmethod
from typing import Optional, Callable

class TransportStrategy(ABC):
    """
    Abstract Base Class for Communication Strategies.
    Allows decoupling Logic from Hardware (UART, WiFi, Mock).
    """

    @abstractmethod
    def connect(self) -> bool:
        """Establishes the connection."""
        pass

    @abstractmethod
    def disconnect(self):
        """Closes the connection."""
        pass

    @abstractmethod
    def send(self, data: bytes) -> bool:
        """Sends raw bytes."""
        pass

    @abstractmethod
    def set_callback(self, callback: Callable[[bytes], None]):
        """Sets the function to call when data is received."""
        pass

    @abstractmethod
    def start(self):
        """Starts the listening loop (if threaded)."""
        pass
        
    @abstractmethod
    def stop(self):
        """Stops the listening loop."""
        pass
