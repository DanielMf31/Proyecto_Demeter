import asyncio
import websockets
import json
import logging
import httpx
import os

# Configuration from environment variables
WS_URL = os.environ.get("DEMETER_WS_URL", "ws://tu-dominio.com/ws/pi")
CORE_URL = os.environ.get("DEMETER_CORE_URL", "http://demeter-core:8000")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DemeterWSClient")

async def handle_message(message):
    try:
        data = json.loads(message)
        logger.info(f"Received message: {data}")
        
        # Example: {"action": "ON", "pin": 4, "target_id": 1}
        if "action" in data and "pin" in data:
            payload = {
                "type": "GPIO_CMD",
                "target_id": data.get("target_id", 1),
                "pin": data["pin"],
                "action": data["action"]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{CORE_URL}/command/gpio", json=payload)
                logger.info(f"Forwarded to core: {response.status_code} - {response.text}")
                
    except Exception as e:
        logger.error(f"Error handling message: {e}")

async def listen():
    logger.info(f"Connecting to WebSocket at {WS_URL}...")
    while True:
        try:
            async with websockets.connect(WS_URL) as websocket:
                logger.info("Connected to WebSocket server.")
                async for message in websocket:
                    await handle_message(message)
        except Exception as e:
            logger.error(f"WebSocket Connection Error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen())
