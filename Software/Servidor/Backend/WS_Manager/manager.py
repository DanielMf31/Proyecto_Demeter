"""
manager.py — Pure connection registry.

Single responsibility: maintain the dict {client_id → WebSocket}
and provide send/broadcast helpers. No business logic here.
"""

from typing import Dict
from fastapi import WebSocket
from Core.logger import setup_logger

logger = setup_logger("ws_registry")


class ConnectionRegistry:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str) -> None:
        await websocket.accept()
        self.active[client_id] = websocket
        logger.info(f"Connected: '{client_id}' | total={len(self.active)}")

    def disconnect(self, client_id: str) -> None:
        if client_id in self.active:
            del self.active[client_id]
            logger.info(f"Disconnected: '{client_id}' | total={len(self.active)}")

    def is_connected(self, client_id: str) -> bool:
        return client_id in self.active

    async def send(self, client_id: str, payload: dict) -> None:
        """Send a JSON payload to a specific client. No-op if not connected."""
        ws = self.active.get(client_id)
        if ws is None:
            logger.warning(f"send() — '{client_id}' not connected, dropping message.")
            return
        try:
            await ws.send_json(payload)
        except Exception as exc:
            logger.error(f"send() error for '{client_id}': {exc}")
            self.disconnect(client_id)

    async def broadcast(self, payload: dict) -> None:
        """Send a JSON payload to all connected clients."""
        for client_id in list(self.active):
            await self.send(client_id, payload)

    async def broadcast_except(self, exclude_id: str, payload: dict) -> None:
        """Send a JSON payload to all clients except the one specified.
        Used by the dispatcher to forward gateway telemetry to frontends
        without echoing back to the Raspberry itself.
        """
        for client_id in list(self.active):
            if client_id != exclude_id:
                await self.send(client_id, payload)


# Singleton used across the app
registry = ConnectionRegistry()
