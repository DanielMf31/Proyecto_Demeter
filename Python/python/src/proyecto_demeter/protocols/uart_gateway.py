import serial
import time
import threading
import queue
import logging
from .protocol_v2 import DemeterProtocolV2

class UartGateway(threading.Thread):
    """
    Handles Serial communication with the ESP32 Gateway.
    Runs in a dedicated thread to avoid blocking the UI.
    """
    def __init__(self, port='/dev/serial0', baud=115200, protocol_engine=None):
        super().__init__()
        self.port = port
        self.baud = baud
        self.serial_conn = None
        self.running = False
        self.send_queue = queue.Queue()
        self.protocol = protocol_engine or DemeterProtocolV2()
        self.logger = logging.getLogger("UartGateway")
        self.message_callback = None # Function to call when valid frame arrives

    def connect(self):
        try:
            self.serial_conn = serial.Serial(self.port, self.baud, timeout=0.1)
            self.logger.info(f"Connected to Gateway at {self.port}")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Failed to connect to {self.port}: {e}")
            return False

    def send_frame(self, frame: bytes):
        """Enqueues a binary frame for transmission."""
        self.send_queue.put(frame)

    def set_callback(self, callback):
        self.message_callback = callback

    def run(self):
        self.running = True
        self.logger.info("Gateway Thread Started")
        
        rx_buffer = b''
        
        while self.running:
            if not self.serial_conn or not self.serial_conn.is_open:
                time.sleep(1)
                continue

            # 1. Transmission (Tx)
            while not self.send_queue.empty():
                try:
                    frame = self.send_queue.get_nowait()
                    self.serial_conn.write(frame)
                    self.logger.debug(f"TX ({len(frame)}B): {frame.hex(' ')}")
                except Exception as e:
                    self.logger.error(f"TX Error: {e}")

            # 2. Reception (Rx)
            try:
                if self.serial_conn.in_waiting > 0:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                    rx_buffer += chunk
                    
                    # Try to parse frames from buffer
                    # This is a naive implementation; in prod use a sliding window
                    # For V2, we look for SYNC (0xFE)
                    while b'\xFE' in rx_buffer:
                        start_idx = rx_buffer.find(b'\xFE')
                        # Discard garbage before sync
                        if start_idx > 0:
                            rx_buffer = rx_buffer[start_idx:]
                        
                        # We need at least Header size to know length
                        if len(rx_buffer) >= 6: # Header size
                            # Peek length (Byte 1)
                            payload_len = rx_buffer[1]
                            total_len = 6 + payload_len + 1 # Header + Payload + CRC
                            
                            if len(rx_buffer) >= total_len:
                                full_frame = rx_buffer[:total_len]
                                rx_buffer = rx_buffer[total_len:] # Remove from buffer
                                
                                # Parse
                                msg = self.protocol.parse_frame(full_frame)
                                if msg and self.message_callback:
                                    self.message_callback(msg)
                            else:
                                break # Wait for more data
                        else:
                            break # Wait for more data
                            
            except Exception as e:
                self.logger.error(f"RX Error: {e}")
                
            time.sleep(0.01)

    def stop(self):
        self.running = False
        if self.serial_conn:
            self.serial_conn.close()
