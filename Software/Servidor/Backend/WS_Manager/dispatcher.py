"""
dispatcher.py — Hub de mensajes del WebSocket backend.

Responsabilidades ÚNICAS tras el refactor:
  1. start_redis_listener()   — Task en background: escucha Redis y reenvía
                                comandos a la Raspberry vía WS.
  2. handle_gateway_message() — Procesa mensajes ENTRANTES desde la Raspberry
                                (ACKs, telemetría) y los retransmite al
                                frontend si hay alguno conectado.

El Frontend ya NO envía comandos por WS. Usa POST /api/command → Redis.

Flujo completo:
  Frontend         Backend (aquí)          Raspberry
     │                  │                      │
     │ POST /api/cmd     │                      │
     │─────────────────▶│ redis.publish()       │
     │                  │──────────────────────▶│ (listener)
     │                  │ registry.send(GW, cmd)│
     │                  │──────────────────────▶│ → UART → ESP32
     │                  │                      │
     │                  │◀─────────────────────│ TempHumReport / Ack / Nack
     │                  │  handle_gateway_msg() │
     │◀─────────────────│ registry.send(FE, ...) │
"""

import asyncio
import json
from pydantic import TypeAdapter, ValidationError
from Core.logger import setup_logger
from Core.redis import redis_manager
from .manager import registry
from schemas import (
    AnyDemeterCommand,
    TempHumReport,
    PinReport,
    SystemReport,
    Ack,
    Nack,
)

logger = setup_logger("dispatcher")

GATEWAY_ID    = "raspberry_gateway"
REDIS_CHANNEL = "demeter:commands"

# TypeAdapter reutilizable — mismo que usa command_router.py para publicar
_cmd_adapter: TypeAdapter[AnyDemeterCommand] = TypeAdapter(AnyDemeterCommand)


# ── Gateway (Raspberry) message handler ──────────────────────────────────────

async def handle_gateway_message(data: dict) -> None:
    """
    Procesa mensajes entrantes DESDE la Raspberry.

    La Raspberry puede enviar:
      - Telemetría: temp_hum_report, pin_report, system_report
      - Confirmaciones: ack, nack
      - Control: ping

    Todo se retransmite al frontend conectado (si existe).
    """
    msg_type = data.get("type")

    # ── Ping / keepalive ──────────────────────────────────────────────────────
    if msg_type == "ping":
        await registry.send(GATEWAY_ID, {"type": "pong"})
        return

    # ── System Config (Discovery) ─────────────────────────────────────────────
    if msg_type == "system_config":
        devices = data.get("devices", {})
        logger.info(f"Received system config from gateway: {len(devices)} device types found.")
        if redis_manager.redis:
            await redis_manager.redis.set("demeter:discovery:config", json.dumps(devices))
            logger.debug("System config stored in Redis.")
        return

    # ── ACK / NACK ────────────────────────────────────────────────────────────
    if msg_type in ("ack", "nack"):
        logger.info(f"Gateway {msg_type}: {data}")
        await registry.broadcast_except(GATEWAY_ID, {
            "type": "gateway_ack",
            "status": msg_type,
            "data": data,
        })
        return

    # ── Telemetría ────────────────────────────────────────────────────────────
    if msg_type == "temp_hum_report":
        try:
            report = TempHumReport(**data)
            logger.info(
                f"TH report — nodo {report.node_id}: "
                f"{report.temperature}°C / {report.humidity}%"
            )
            await registry.broadcast_except(GATEWAY_ID, {
                "type": "telemetry",
                "sensor": "temp_hum",
                "data": report.model_dump(),
            })
        except Exception as exc:
            logger.error(f"temp_hum_report parse error: {exc}")
        return

    if msg_type == "pin_report":
        try:
            report = PinReport(**data)
            logger.info(
                f"Pin report — nodo {report.node_id}: "
                f"pin {report.pin} = {report.state}"
            )
            await registry.broadcast_except(GATEWAY_ID, {
                "type": "telemetry",
                "sensor": "pin",
                "data": report.model_dump(),
            })
        except Exception as exc:
            logger.error(f"pin_report parse error: {exc}")
        return

    if msg_type == "system_report":
        try:
            report = SystemReport(**data)
            logger.info(
                f"System report — nodo {report.node_id}: "
                f"mode={report.mode} batt={report.battery_mv}mV"
            )
            await registry.broadcast_except(GATEWAY_ID, {
                "type": "telemetry",
                "sensor": "system",
                "data": report.model_dump(exclude={"reserved"}),
            })
        except Exception as exc:
            logger.error(f"system_report parse error: {exc}")
        return

    logger.warning(f"[gateway] Tipo no manejado: '{msg_type}'")


# ── Redis listener (asyncio.Task) ─────────────────────────────────────────────

async def start_redis_listener() -> None:
    """
    Tarea en background (lanzada en startup de app.py).

    Espera a que Redis esté disponible, se suscribe al canal 'demeter:commands'
    y por cada mensaje publicado:
      1. Lo deserializa y valida con Pydantic (AnyDemeterCommand).
      2. Si la Raspberry está conectada → se lo reenvía por WS.
      3. Si no está conectada → avisa a todos los frontends conectados.

    El JSON publicado en Redis tiene el formato directo del modelo Pydantic:
      {"type": "set_gpio", "target_id": 1, "pin": 4, "value": 1, ...}
    """
    logger.info("Redis listener arrancando — esperando a Redis…")
    while not redis_manager.redis:
        await asyncio.sleep(1)

    pubsub = redis_manager.redis.pubsub()
    await pubsub.subscribe(REDIS_CHANNEL)
    logger.info(f"Redis listener suscrito a '{REDIS_CHANNEL}'.")

    try:
        async for raw in pubsub.listen():
            if raw["type"] != "message":
                continue

            # ── Deserializar ──────────────────────────────────────────────────
            try:
                payload_dict = json.loads(raw["data"])
            except (json.JSONDecodeError, TypeError) as exc:
                logger.error(f"Redis listener: JSON inválido — {exc}")
                continue

            # ── Validar con Pydantic ──────────────────────────────────────────
            try:
                cmd = _cmd_adapter.validate_python(payload_dict)
            except ValidationError as exc:
                logger.warning(f"Redis listener: comando inválido — {exc}")
                continue

            cmd_type = cmd.type  # type: ignore[attr-defined]
            logger.debug(f"Redis → [{cmd_type}] target={cmd.target_id}")

            # ── Despachar a la Raspberry ──────────────────────────────────────
            if registry.is_connected(GATEWAY_ID):
                # Enviamos el JSON completo (con `type`) para que la Raspberry
                # use el mismo discriminador al deserializar en su lado.
                await registry.send(GATEWAY_ID, cmd.model_dump())
                logger.info(f"Despachado [{cmd_type}] → {GATEWAY_ID}")
            else:
                logger.warning(
                    f"Raspberry no conectada — comando [{cmd_type}] descartado."
                )
                await registry.broadcast_except(GATEWAY_ID, {
                    "type": "dispatcher_status",
                    "status": "gateway_offline",
                    "message": (
                        f"Comando '{cmd_type}' descartado: "
                        "la Raspberry no está conectada."
                    ),
                })

    except asyncio.CancelledError:
        logger.info("Redis listener cancelado.")
    except Exception as exc:
        logger.error(f"Redis listener error fatal: {exc}", exc_info=True)
    finally:
        await pubsub.unsubscribe(REDIS_CHANNEL)
        logger.info("Redis listener desuscrito.")
