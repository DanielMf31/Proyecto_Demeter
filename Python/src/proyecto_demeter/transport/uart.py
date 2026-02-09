import serial
import threading
import time
import logging
from .interface import TransportStrategy
from ..core.device_manager import DeviceManager

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
            self.serial_conn.flushInput() # Clear startup garbage
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
        """
        Thread loop for receiving data.
        Implements a buffering mechanism to handle stream fragmentation.
        """
        self.logger.info("Listening Thread Started")
        
        rx_buffer = b''
        SYNC_BYTE = b'\xfe' # Must match ProtocolV2
        HEADER_SIZE = 6     # Must match ProtocolV2
        
        while self.running:
            try:
                if self.serial_conn and self.serial_conn.is_open:
                    # Read available bytes
                    if self.serial_conn.in_waiting > 0:
                        chunk = self.serial_conn.read(self.serial_conn.in_waiting)
                        rx_buffer += chunk
                        
                        # Process Buffer
                        while len(rx_buffer) >= HEADER_SIZE:
                            # 1. Search for Sync Byte
                            try:
                                sync_idx = rx_buffer.index(SYNC_BYTE)
                            except ValueError:
                                # No sync byte found in the entire buffer
                                # Keep the last few bytes just in case split sync?
                                # No, sync is 1 byte.
                                # Discard all but last byte? 
                                # Safer: Discard all.
                                self.logger.debug(f"Discarding garbage: {rx_buffer.hex()}")
                                rx_buffer = b''
                                break
                            
                            # Align buffer to Sync
                            if sync_idx > 0:
                                self.logger.debug(f"Discarding {sync_idx} garbage bytes: {rx_buffer[:sync_idx].hex()}")
                                rx_buffer = rx_buffer[sync_idx:]
                                
                            # 2. Check for Header (again, after alignment)
                            if len(rx_buffer) < HEADER_SIZE:
                                break # Wait for more data
                                
                            # 3. Extract Length (Byte 1 is Length)
                            # Header: [SYNC] [LEN] [FLAGS] [SRC] [DST] [CMD]
                            payload_len = rx_buffer[1]
                            total_frame_len = HEADER_SIZE + payload_len + 1 # +1 for CRC
                            
                            # 4. Check for Full Frame
                            if len(rx_buffer) < total_frame_len:
                                break # Wait for more data
                                
                            # 5. Extract Frame
                            frame = rx_buffer[:total_frame_len]
                            rx_buffer = rx_buffer[total_frame_len:] # Remove from buffer
                            
                            # 6. Dispatch
                            if self.callback:
                                try:
                                    self.callback(frame)
                                except Exception as cb_err:
                                     self.logger.error(f"Callback Error: {cb_err}")

                    else:
                        time.sleep(0.01) # Yield if no data
                else:
                    time.sleep(0.1) # Wait for connection
                    
            except Exception as e:
                self.logger.error(f"RX Loop Error: {e}")
                time.sleep(1) # Prevent tight loop on error
