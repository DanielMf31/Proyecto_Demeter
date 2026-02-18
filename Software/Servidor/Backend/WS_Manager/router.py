from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from .manager import manager
from Core.logger import setup_logger
from schemas import SetGpio, CmdId # Import Protocol Models

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
            
            elif msg_type == "GPIO_CMD":
                # Translate Frontend Command -> Protocol V2 (SetGpio)
                try:
                    target_id = data.get("target_id", 2)
                    pin = data.get("pin")
                    action = data.get("action")
                    value = 1 if action == "ON" else 0
                    
                    # Create Strict Protocol Command
                    cmd = SetGpio(
                        target_id=target_id,
                        source_id=1, # Backend ID
                        pin=pin,
                        value=value
                    )
                    
                    # Convert to Dict for JSON transport
                    # Important: We must include the "type" or structure the Gateway expects.
                    # The Gateway's _parse_json_command uses DemeterProtocolV2.validate_json_message
                    # which likely checks for fields matching the model.
                    # We send the model dump directly.
                    payload = cmd.model_dump()
                    # We might need to inject 'cmd_id' if model_dump doesn't include it by default (it's a method)
                    # or if the validator uses it. ideally 'type' field in JSON is needed? 
                    # Reader of code: _parse_json_command checks data structure.
                    # Let's verify SetGpio structure. It has target_id, source_id, pin, value, flags.
                    
                    # We add a 'type' field just in case the dispatcher checks it for routing, 
                    # but strictly speaking the Pydantic model validation relies on fields.
                    # However, to be safe and clear, we send the dict.
                    
                    logger.info(f"Translating GPIO_CMD to Protocol V2: {payload}")
                    
                    target_client = "raspberry_gateway"
                     # Check if Gateway is connected locally
                    if target_client in manager.active_connections:
                        await manager.send_personal_message(payload, target_client)
                        await manager.send_personal_message({"status": "OK", "message": "Command Sent to Gateway"}, client_id)
                    else:
                        # Fallback to Redis
                         if redis_manager.redis:
                            await redis_manager.publish_event("command", payload)
                         else:
                            await manager.send_personal_message({"status": "ERROR", "message": "Gateway Offline"}, client_id)

                except Exception as e:
                    logger.error(f"Translation Error: {e}")
                    await manager.send_personal_message({"status": "ERROR", "message": f"Invalid Command: {e}"}, client_id)            
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error(f"WebSocket error for {client_id}: {e}")
        manager.disconnect(client_id)
