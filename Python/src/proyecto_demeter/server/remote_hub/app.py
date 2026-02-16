from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import logging
import json

app = FastAPI(title="Demeter Remote Hub")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RemoteHub")

# Store active Raspberry Pi connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Raspberry Pi client connected")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("Raspberry Pi client disconnected")

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

class Command(BaseModel):
    pin: int
    action: str
    target_id: int = 1

@app.post("/command")
async def receive_command(cmd: Command):
    logger.info(f"Received command from UI: {cmd}")
    
    if not manager.active_connections:
        raise HTTPException(status_code=503, detail="No Raspberry Pi connected")
    
    # Relay message to all connected Pis (or target specific one if needed)
    await manager.broadcast(cmd.dict())
    return {"status": "dispatched", "target_count": len(manager.active_connections)}

@app.websocket("/ws/pi")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, we can also receive telemetry here
            data = await websocket.receive_text()
            logger.info(f"Telemetry from Pi: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
