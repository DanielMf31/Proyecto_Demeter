"""
command_router.py — Endpoint HTTP para envío de comandos al hardware.

Ruta: POST /api/command

Flujo:
  Frontend → POST /api/command (JSON con `type`)
      │
      ▼
  Pydantic valida con TypeAdapter(AnyDemeterCommand)
      │
      ▼
  redis.publish("demeter:commands", json)
      │
      ▼
  start_redis_listener() (tarea en background, ya corriendo)
      │
      ▼
  registry.send("raspberry_gateway", cmd)  → Raspberry WS → UART → ESP32

Ventajas sobre WS desde el Frontend:
  - Sin gestión de reconexión ni heartbeats en el browser.
  - Respuesta HTTP inmediata con estado del encolado.
  - Fácilmente testeable con curl / Swagger.
  - El WS queda reservado exclusivamente para Raspberry ↔ Backend.
"""

import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import TypeAdapter, ValidationError

from Core.redis import redis_manager
from WS_Manager.manager import registry

# Importamos el TypeAdapter y el Union discriminado desde schemas
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "Common"))

from schemas import AnyDemeterCommand

from Core.auth import get_current_active_user
from BD.models import User

logger = logging.getLogger("command_router")

router = APIRouter()

# Canal Redis — mismo canal que escucha start_redis_listener()
REDIS_CHANNEL = "demeter:commands"
GATEWAY_ID    = "raspberry_gateway"

# TypeAdapter reutilizable (se construye una vez al importar el módulo)
_cmd_adapter: TypeAdapter[AnyDemeterCommand] = TypeAdapter(AnyDemeterCommand)


@router.post(
    "/command",
    summary="Enviar un comando al hardware",
    description="""
Acepta cualquier comando del protocolo Demeter en formato JSON.
El campo **`type`** es obligatorio y actúa como discriminador:

| type | Descripción |
|---|---|
| `set_gpio` | Activar/desactivar un pin digital |
| `set_pwm`  | Controlar un pin PWM |
| `exec_sequence` | Ejecutar una secuencia de pasos |
| `ping` | Verificar conectividad con un nodo |
| `get_sensors` | Solicitar lectura de sensores |

El comando se publica en Redis y es despachado a la Raspberry vía WebSocket.

**Requiere autenticación**. Sólo usuarios con rol `admin` u `operator` pueden ejecutar.
    """,
    status_code=status.HTTP_202_ACCEPTED,
)
async def post_command(body: dict, current_user: User = Depends(get_current_active_user)) -> dict:
    """
    Recibe un JSON con `type` discriminador, lo valida con Pydantic
    y lo publica en Redis para que el listener lo reenvíe a la Raspberry.
    """
    if current_user.role not in ["admin", "operator"]:
        logger.warning(f"Intento de comando bloqueado para el usuario {current_user.username} (Rol: {current_user.role})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilegios insuficientes para enviar comandos."
        )

    # ── 1. Validar con el TypeAdapter discriminado ────────────────────────────
    try:
        cmd = _cmd_adapter.validate_python(body)
    except ValidationError as exc:
        logger.warning(f"POST /api/command — validación fallida: {exc}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )

    cmd_type = cmd.type  # type: ignore[attr-defined]
    logger.info(f"POST /api/command — tipo={cmd_type} target={cmd.target_id}")

    # ── 2. Publicar en Redis ──────────────────────────────────────────────────
    if not redis_manager.redis:
        logger.error("Redis no disponible — comando descartado.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "error",
                "message": "Redis no disponible. El servidor no puede enrutar comandos.",
            },
        )

    # Serializamos el modelo completo (incluye `type`) para que el listener
    # de la Raspberry pueda usar el mismo discriminador al deserializar.
    payload_json = cmd.model_dump_json()
    await redis_manager.redis.publish(REDIS_CHANNEL, payload_json)
    logger.debug(f"Publicado en Redis [{REDIS_CHANNEL}]: {payload_json}")

    # ── 3. Caché de Estado y Registro de Actividad (Batch) ────────────────────
    if cmd_type == "set_gpio":
        # Guardamos en caché por 60s
        await redis_manager.cache_device_state(cmd.pin, bool(cmd.value)) # type: ignore[attr-defined]
        
        # Encolamos para guardado por lotes en DB (ActivityLog)
        await redis_manager.push_activity_event({
            "action_type": "button_press",
            "device_id": cmd.pin, # Por ahora usamos pin como device_id simplificado
            "description": f"Manual toggle Node:{cmd.target_id} Pin:{cmd.pin} -> {cmd.value}", # type: ignore[attr-defined]
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

    # ── 4. Informar al frontend si la Raspberry está conectada ───────────────
    gateway_online = registry.is_connected(GATEWAY_ID)
    if not gateway_online:
        logger.warning(f"Comando publicado pero la Raspberry no está conectada.")

    return {
        "status": "queued" if gateway_online else "gateway_offline",
        "message": (
            f"Comando '{cmd_type}' encolado correctamente."
            if gateway_online
            else f"Comando '{cmd_type}' encolado, pero la Raspberry no está conectada."
        ),
        "command_type": cmd_type,
    }
