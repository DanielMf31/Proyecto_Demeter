"""
discovery_router.py — Endpoint de descubrimiento de dispositivos.

Este router permite al frontend conocer qué dispositivos (bombas, válvulas, etc.)
hay conectados y configurados en la Raspberry sin tener que hardcodearlos.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Depends
from Core.redis import redis_manager
from Core.auth import get_current_active_user
from BD.models import User

logger = logging.getLogger("discovery_router")
router = APIRouter()

REDIS_KEY = "demeter:discovery:config"

@router.get(
    "/devices",
    summary="Listar dispositivos descubiertos",
    description="Retorna el mapeo de hardware reportado por la Raspberry Pi."
)
async def get_devices(current_user: User = Depends(get_current_active_user)):
    """
    Lee la configuración guardada en Redis y la retorna.
    Si no hay configuración (Raspberry no conectada aún), retorna un error 404.
    """
    if not redis_manager.redis:
        raise HTTPException(status_code=503, detail="Redis no disponible")

    raw_config = await redis_manager.redis.get(REDIS_KEY)
    
    if not raw_config:
        # Podríamos retornar una lista vacía, pero un 404 indica que
        # el origen de la verdad (Raspberry) no ha reportado nada aún.
        raise HTTPException(status_code=404, detail="No hay configuración de dispositivos disponible.")

    try:
        devices = json.loads(raw_config)
        return {
            "status": "online",
            "devices": devices
        }
    except Exception as exc:
        logger.error(f"Error parsing discovery config from Redis: {exc}")
        raise HTTPException(status_code=500, detail="Error al procesar la configuración")
