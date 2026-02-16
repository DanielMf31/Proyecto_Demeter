import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MockWSServer")

async def handler(websocket, path):
    logger.info("Client connected")
    try:
        # Send a test command immediately
        test_cmd = {
            "action": "ON",
            "pin": 4,
            "target_id": 1
        }
        logger.info(f"Sending test command: {test_cmd}")
        await websocket.send(json.dumps(test_cmd))
        
        # Keep connection alive
        async for message in websocket:
            logger.info(f"Received from client: {message}")
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Client disconnected")

async def main():
    server = await websockets.serve(handler, "0.0.0.0", 8765)
    logger.info("Mock WebSocket Server started on ws://0.0.0.0:8765")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
