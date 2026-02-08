import serial
import threading
import time
import logging
from .interface import TransportStrategy
from proyecto_demeter.protocols.device_manager import DeviceManager

class UartTransport(TransportStrategy, threading.Thread):
    """
    Concrete implementation of TransportStrategy using Serial (UART).
    
    Runs a background thread to continuously listen for incoming data (`RX`)
    while allowing thread-safe transmission (`TX`) from the main thread.
    
    Attributes:
        port (str): Serial port path (e.g., '/dev/ttyUSB0').
        baud (int): Baud rate (default: 115200).
        callback (callable): Function to invoke when data is received.
    """
    def __init__(self, port: str = None, baud_rate: int = None):
        super().__init__()
        self.logger = logging.getLogger("UartTransport")
        
        self.port = port
        self.baud = baud_rate

        # Only load DeviceManager if config is missing and we don't have explicit args
        if not self.port or not self.baud:
            try:
                self.dev_mgr = DeviceManager()
                if not self.port: self.port = self.dev_mgr.get_config("serial_port")
                if not self.baud: self.baud = self.dev_mgr.get_config("baud_rate")
            except Exception:
                pass # Fallback to defaults
        
        # Defaults
        if not self.port: self.port = '/dev/serial0'
        if not self.baud: self.baud = 115200

        self.serial_conn = None
        self.running = False
        self.callback = None
        
    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=0.1)
            self.logger.info(f"Connected to UART at {self.port} ({self.baud})")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False

    def disconnect(self):
        self.stop()
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.logger.info("Disconnected UART")

    def send(self, data: bytes) -> bool:
        if not self.serial_conn or not self.serial_conn.is_open:
            self.logger.warning("Attempted to send on closed UART")
            return False
        try:
            self.serial_conn.write(data)
            self.logger.debug(f"TX: {data.hex()}")
            return True
        except Exception as e:
            self.logger.error(f"TX Error: {e}")
            return False

    def set_callback(self, callback):
        self.callback = callback

    def start(self):
        if not self.running:
            self.running = True
            super().start() # Thread.start()

    def stop(self):
        self.running = False
        if self.is_alive():
            self.join(timeout=1.0)

    def run(self):
        """Thread loop for receiving data."""
        self.logger.info("Listening Thread Started")
        while self.running:
            if self.serial_conn and self.serial_conn.is_open and self.serial_conn.in_waiting > 0:
                try:
                    # Read all available
                    data = self.serial_conn.read(self.serial_conn.in_waiting)
                    if data and self.callback:
                        self.callback(data)
                except Exception as e:
                    self.logger.error(f"RX Error: {e}")
            
            time.sleep(0.01)
