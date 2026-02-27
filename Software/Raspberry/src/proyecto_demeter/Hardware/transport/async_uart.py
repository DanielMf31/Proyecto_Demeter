import asyncio
import logging
import serial_asyncio
from typing import Callable, Optional

from .interface import TransportStrategy

class AsyncUartTransport(TransportStrategy):
    """
    AsyncIO Transport for Serial Communication.
    Uses 'pyserial-asyncio' to handle UART without blocking the event loop.
    """
    def __init__(self, port: str = None, baud: int = 115200, rx_callback: Optional[Callable[[bytes], None]] = None):
        self.port = port or "/dev/ttyUSB0"
        self.baud = baud
        self.rx_callback = rx_callback
        self.reader = None
        self.writer = None
        self.logger = logging.getLogger("AsyncUart")
        self.read_task = None
        self.write_task = None
        self.tx_queue = asyncio.Queue()

    async def connect(self) -> bool:
        """Creates the serial connection and starts the reading loop."""
        self.logger.info(f"Connecting to {self.port} @ {self.baud}...")
        try:
            self.reader, self.writer = await serial_asyncio.open_serial_connection(
                url=self.port, baudrate=self.baud
            )
            self.logger.info("Connected to UART (Async).")
            self.start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            return False

    def start(self):
        """Starts background reading and writing tasks."""
        if not self.read_task:
            self.read_task = asyncio.create_task(self._read_loop())
        if not self.write_task:
            self.write_task = asyncio.create_task(self._write_loop())

    def stop(self):
        """Stops background tasks."""
        if self.read_task:
            self.read_task.cancel()
            self.read_task = None
        if self.write_task:
            self.write_task.cancel()
            self.write_task = None

    def set_callback(self, callback: Callable[[bytes], None]):
        self.rx_callback = callback

    async def disconnect(self):
        """Closes the connection."""
        self.stop()
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.logger.info("UART Closed.")

    async def _read_loop(self):
        """Continuously reads bytes from UART."""
        while True:
            try:
                # Read chunks (up to 1024 bytes)
                data = await self.reader.read(1024)
                if data:
                    # self.logger.debug(f"RX Raw: {data.hex()}")
                    if self.rx_callback:
                        self.rx_callback(data)
                else:
                    # EOF or Disconnect?
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Read Error: {e}")
                await asyncio.sleep(1)

    async def _write_loop(self):
        """Consumes messages from the TX queue and sends them."""
        while True:
            try:
                data = await self.tx_queue.get()
                if self.writer:
                    self.writer.write(data)
                    await self.writer.drain()
                    self.logger.debug(f"TX: {data.hex()}")
                self.tx_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Write Loop Error: {e}")
                await asyncio.sleep(0.1)

    async def send(self, data: bytes) -> bool:
        """Enqueues bytes to be sent asynchronously."""
        try:
            await self.tx_queue.put(data)
            return True
        except Exception as e:
            self.logger.error(f"Send Error (Values): {e}")
            return False
        
    # Legacy close method to call disconnect for compatibility if needed
    async def close(self):
        await self.disconnect()
