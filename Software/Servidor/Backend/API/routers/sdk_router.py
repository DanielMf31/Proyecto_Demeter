import logging
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Core.database import get_db
from Core.auth import get_api_key_or_403
from BD.models import Experiment, TelemetryAmbient
from Core.redis import redis_manager

logger = logging.getLogger("sdk_router")
router = APIRouter(prefix="/sdk", tags=["SDK Integration"])

@router.get("/mediciones/{experimento_id}", summary="Fetch Raw Telemetry Data for SDK")
async def get_sdk_measurements(
    experimento_id: int,
    dias: int = 30,
    experiment: Experiment = Depends(get_api_key_or_403),
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna toda la telemetría en crudo (JSON) de las plantas/nodos 
    pertenecientes a este experimento, delimitado por una cantidad de días.
    Endpoint protegido exclusivamente por X-API-Key.
    """
    try:
        # 1. Intentar Caché Rápido en Redis si está disponible 
        # (El caché general se puebla al generar el crudo)
        if redis_manager.redis:
            cache_key = f"demeter:raw_data:experimento_{experimento_id}"
            cached_data = await redis_manager.redis.get(cache_key)
            if cached_data:
                logger.debug(f"[SDK] Hit REDIS Cache for Exp {experimento_id}")
                data_list = json.loads(cached_data)
                
                # Filtrar en memoria por días si es menor a los 6 meses de caché
                limit_date = datetime.utcnow() - timedelta(days=dias)
                filtered_data = [
                    d for d in data_list 
                    # asume que el json cacheado tiene 'timestamp' iso string
                    if datetime.fromisoformat(d['timestamp'].replace("Z", "+00:00")).replace(tzinfo=None) >= limit_date
                ]
                return filtered_data

        # 2. Respaldo (Fallback a Postgres) si no hay caché
        logger.debug(f"[SDK] Miss Cached Data. Querying DB directly for Exp {experimento_id}")
        nodes = [p.node_id for p in experiment.plants]
        if not nodes:
            return []
            
        limit_date = datetime.utcnow() - timedelta(days=dias)
        
        query = select(TelemetryAmbient).where(
            TelemetryAmbient.node_id.in_(nodes),
            TelemetryAmbient.timestamp >= limit_date
        ).order_by(TelemetryAmbient.timestamp.asc())
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        data = [
            {
                "timestamp": r.timestamp.isoformat(),
                "node_id": r.node_id,
                "temperature": r.air_temperature,
                "humidity": r.air_humidity
            } for r in records
        ]
        return data

    except Exception as e:
        logger.error(f"[SDK] Error fetching measurements: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data from server.")
