from abc import ABC, abstractmethod
from typing import Optional, Callable

class TransportStrategy(ABC):
    """
    Abstract Base Class for Communication Strategies.
    
    Defines the contract for any transport layer (UART, TCP/IP, LoRa, Mock),
    ensuring the upper logic layers remain agnostic to the physical medium.
    
    Methods:
        connect(): Establish connection.
        send(data): Transmit raw bytes.
        set_callback(cb): Register data reception handler.
        start()/stop(): Manage background listening tasks.
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
