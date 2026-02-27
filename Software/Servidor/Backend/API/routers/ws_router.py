"""
ws_router.py — Capa de transporte WebSocket.

Responsabilidad única: gestionar conexiones WS y delegar mensajes.

Conexiones esperadas:
  /ws/raspberry_gateway  →  Raspberry Pi (bidireccional)
                             · Recibe: comandos despachados desde Redis
                             · Envía:  telemetría, ACK, NACK

  /ws/{cualquier_id}     →  Frontend u otro cliente (opcional, solo lectura)
                             · Recibe: telemetría retransmitida por el dispatcher
                             · Envía:  nada (los comandos van por HTTP POST)

El frontend NO necesita conectarse por WS para enviar comandos.
Usa POST /api/command en su lugar.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from WS_Manager.manager import registry
from WS_Manager.dispatcher import handle_gateway_message, GATEWAY_ID
from Core.logger import setup_logger

router = APIRouter()
logger = setup_logger("ws_router")


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Punto de entrada único para todas las conexiones WebSocket.

    - Si client_id == "raspberry_gateway":
        Acepta mensajes entrantes (telemetría, ACKs) y los procesa.
    - Cualquier otro client_id (frontend, monitoring, etc.):
        Se registra en el registry para recibir push de telemetría,
        pero sus mensajes entrantes se ignoran (debe usar HTTP).
    """
    await registry.connect(websocket, client_id)
    is_gateway = (client_id == GATEWAY_ID)

    if is_gateway:
        logger.info(" Raspberry Gateway conectada.")
    else:
        logger.info(f" Cliente '{client_id}' conectado (modo solo-recepción).")

    try:
        while True:
            # Recibimos el mensaje (ambos tipos de cliente pueden enviar)
            data = await websocket.receive_json()

            if is_gateway:
                # La Raspberry envía telemetría y confirmaciones → procesar
                await handle_gateway_message(data)
            else:
                # El frontend no debería enviar nada por aquí.
                # Si lo hace, informamos amablemente del cambio de API.
                logger.debug(
                    f"[ws/{client_id}] Mensaje ignorado "
                    f"(usa POST /api/command): {data.get('type', '?')}"
                )
                await registry.send(client_id, {
                    "type": "info",
                    "message": "Para enviar comandos usa POST /api/command. "
                               "Este canal WS es solo para recibir telemetría.",
                })

    except WebSocketDisconnect:
        registry.disconnect(client_id)
        if is_gateway:
            logger.warning("⚡ Raspberry Gateway desconectada.")
        else:
            logger.info(f"Cliente '{client_id}' desconectado.")

    except Exception as exc:
        logger.error(f"WS error para '{client_id}': {exc}", exc_info=True)
        registry.disconnect(client_id)
