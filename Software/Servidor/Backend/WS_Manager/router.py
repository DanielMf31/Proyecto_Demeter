from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from .manager import manager
from Core.logger import setup_logger

router = APIRouter()
logger = setup_logger("ws_router")

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    # Handshake / Auth logic could go here
    # verify_token(token)
    
    await manager.connect(websocket, client_id)
    try:
        from Core.redis import redis_manager
        
        while True:
            data = await websocket.receive_json()
            logger.debug(f"Received from {client_id}: {data}")
            
            msg_type = data.get("type")

            if msg_type == "ping":
                await manager.send_personal_message({"type": "pong"}, client_id)
            
            elif msg_type == "command" or msg_type == "GPIO_CMD" or msg_type == "TOGGLE_PIN":
                # Strategy:
                # 1. Try to send directly to connected Gateway (if on this instance)
                # 2. Fallback to Redis (if scaled)
                
                target_client = "raspberry_gateway"
                
                # Check if Gateway is connected locally
                if target_client in manager.active_connections:
                    logger.info(f"Direct routing command from {client_id} to Gateway")
                    await manager.send_personal_message(data, target_client)
                    # Ack to sender
                    await manager.send_personal_message({"status": "OK", "message": "Routed to Gateway"}, client_id)
                else:
                    # Gateway not local, try Redis if available
                    try:
                        if redis_manager.redis:
                            logger.info(f"Publishing command from {client_id} to Redis: {data}")
                            await redis_manager.publish_event("command", data)
                        else:
                            logger.warning("Gateway not connected and Redis unavailable.")
                            await manager.send_personal_message({"status": "ERROR", "message": "Gateway Offline"}, client_id)
                    except Exception as e:
                         logger.error(f"Redis Publish Error: {e}")

            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
