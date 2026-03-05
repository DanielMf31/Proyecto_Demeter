"""
edge_server.py — Demeter Edge API Server (RPi Local Mode)

Entrypoint dedicado para el modo 'rpi-local'.
Solo se ejecuta cuando DEMETER_ENV=rpi-local.

Levanta un servidor FastAPI con Uvicorn junto al GatewayOrchestrator.
Expone endpoints locales de control de hardware directamente desde la RPi:
  - POST /api/auth/login  (mock, sin autenticación real)
  - GET  /api/devices     (devuelve el mapa de dispositivos del devices.json)
  - POST /api/command     (envía un comando directamente al bus UART)

El GatewayOrchestrator sigue siendo puro y sin dependencias de FastAPI.
"""

import asyncio
import json
import logging
import os

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from proyecto_demeter.Hardware.orchestration.command_dispatcher import GatewayOrchestrator

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
)
logger = logging.getLogger("EdgeServer")

# ── FastAPI App ────────────────────────────────────────────────────────────
app = FastAPI(title="Demeter Edge API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Gateway Orchestrator (singleton) ──────────────────────────────────────
gateway = GatewayOrchestrator()

# ── Routes ────────────────────────────────────────────────────────────────

@app.post("/api/auth/login")
async def mock_login(request: Request):
    """Mock login para el Edge UI local. Sin autenticación real."""
    return {"access_token": "edge_local_token", "token_type": "bearer"}


@app.get("/api/devices")
async def get_devices():
    """Devuelve el mapa de dispositivos cargado desde devices.json."""
    return {
        "status": "online",
        "devices": gateway.device_manager.get_config()
    }


@app.post("/api/command")
async def post_command(request: Request):
    """Envía un comando directamente al bus UART de la Raspberry Pi."""
    try:
        data = await request.json()
        logger.info(f"[Edge API] <-- Petitoria recibida: {data}")
    except Exception:
        logger.error("[Edge API] Error al parsear JSON de la petición")
        return {"error": "Invalid JSON"}

    cmd_model = gateway._parse_incoming_command(data)
    if cmd_model:
        logger.info(f"[Edge API] --> Comando parseado: {type(cmd_model).__name__} (Target: {cmd_model.target_id})")
        await gateway.uart.send_command(cmd_model)
        logger.info(f"[Edge API] OK: Comando enviado al bus UART")
        return {"status": "success"}

    logger.warning(f"[Edge API] FAIL: No se pudo mapear el comando JSON a la especificación Demeter: {data}")
    return {"error": "Invalid command payload"}


# ── Main Loop ──────────────────────────────────────────────────────────────

async def main():
    """
    Ciclo principal del Edge Server:
    1. Arranca el procesador UART en background.
    2. Levanta el servidor Uvicorn con la app FastAPI.
    """
    logger.info("🌱 Demeter Edge Server iniciando (rpi-local mode)…")

    gateway.uart.add_listener(gateway.dispatch_uart_to_ws)
    uart_task = asyncio.create_task(gateway.uart.start())

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())

    # El WS client conecta al servidor remoto si DEMETER_WS_URL está configurado
    ws_url = os.getenv("DEMETER_WS_URL", "")
    if ws_url:
        logger.info(f"Connecting to remote WS: {ws_url}")
        await asyncio.gather(uart_task, api_task, gateway.ws_client.start())
    else:
        logger.info("No DEMETER_WS_URL configured — running in pure local mode (no remote WS)")
        await asyncio.gather(uart_task, api_task)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Edge Server detenido por el usuario.")
