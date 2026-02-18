import asyncio
import logging
import json
import websockets
from typing import Optional, Callable, Awaitable

from configuration import settings

class DemeterWebsocketClient:
    """
    Manages the persistent WebSocket connection to the Backend.
    """
    def __init__(self, on_message_callback: Callable[[str], Awaitable[None]]):
        self.logger = logging.getLogger("WS_Client")
        self.on_message = on_message_callback
        
        # Determine URI
        ws_scheme = "ws"
        if settings.SOCKET_PORT == 443: ws_scheme = "wss"
        self.uri = f"{ws_scheme}://{settings.HOST}:{settings.SOCKET_PORT}/ws/raspberry_gateway"
        
        self.connection = None
        self.running = False
        self._task = None

    async def start(self):
        """Start the connection loop."""
        self.running = True
        self._task = asyncio.create_task(self._connect_loop())
        self.logger.info(f"WS Client background task started. Target: {self.uri}")

    async def stop(self):
        """Stop connection and cancel loop."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        if self.connection:
            await self.connection.close()
            self.connection = None

    async def send_json(self, data: dict):
        """Send JSON payload to the server."""
        if self.connection:
            try:
                await self.connection.send(json.dumps(data))
            except Exception as e:
                self.logger.error(f"Send Error: {e}")
        else:
            self.logger.debug("Attempted to send but WS is disconnected.")

    async def _connect_loop(self):
        """Internal loop for persistent connection."""
        while self.running:
            try:
                async with websockets.connect(self.uri) as ws:
                    self.connection = ws
                    self.logger.info("WebSocket Connected!")
                    
                    # Identity Handshake
                    await ws.send(json.dumps({"type": "identity", "client": "gateway"}))

                    # Read Loop
                    try:
                        async for message in ws:
                            if self.on_message:
                                await self.on_message(message)
                    except websockets.ConnectionClosed:
                        self.logger.warning("WebSocket Connection Closed.")
                    finally:
                        self.connection = None

            except (ConnectionRefusedError, OSError) as e:
                self.logger.warning(f"Connection Failed: {e}. Retrying in 5s...")
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Unexpected WS Error: {e}")
            
            if self.running:
                await asyncio.sleep(5)
