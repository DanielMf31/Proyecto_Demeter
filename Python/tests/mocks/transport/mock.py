import logging
import threading
import time
from .interface import TransportStrategy

class MockTransport(TransportStrategy, threading.Thread):
    """
    Mock implementation of TransportStrategy for testing GUI without hardware.
    Simulates a connection and logs TX data.
    """
    def __init__(self, port="MOCK", baud_rate=0):
        super().__init__()
        self.logger = logging.getLogger("MockTransport")
        self.port = port
        self.baud = baud_rate
        self.running = False
        self.callback = None
        self.logger.info("MockTransport Initialized")

    def connect(self) -> bool:
        self.logger.info(f"Connected to Mock Port {self.port}")
        return True

    def disconnect(self):
        self.logger.info("Disconnected Mock Port")
        self.stop()

    def send(self, data: bytes) -> bool:
        self.logger.info(f"MOCK TX: {data.hex().upper()}")
        # Optional: Simulate Loopback or Response here if needed
        return True

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if not self.running:
            self.running = True
            super().start()

    def stop(self):
        self.running = False
        if self.is_alive():
            self.join(timeout=1.0)

    def run(self):
        self.logger.info("Mock Listening Thread Started")
        while self.running:
            time.sleep(1.0) # Just keep thread alive
