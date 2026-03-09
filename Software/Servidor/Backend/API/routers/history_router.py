from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
import logging

from Core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from Core.auth import get_current_active_user
from BD.models import User, TelemetryAmbient

logger = logging.getLogger("history_router")
router = APIRouter(prefix="/history", tags=["History"])

@router.get("/node/{node_id}", summary="Get 30-day Telemetry History for a Node")
async def get_node_history(
    node_id: int, 
    days: int = 30,
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    """
    Fetches up to `days` (default 30) of telemetry records for a specific node_id.
    """
    try:
        limit_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(TelemetryAmbient).where(
            TelemetryAmbient.node_id == node_id,
            TelemetryAmbient.timestamp >= limit_date
        ).order_by(TelemetryAmbient.timestamp.asc()) # Asegurar orden cronologico para graficas
        
        result = await db.execute(query)
        records = result.scalars().all()
        
        return [{
            "timestamp": r.timestamp.isoformat(),
            "temperature": r.air_temperature,
            "humidity": r.air_humidity
        } for r in records]
        
    except Exception as e:
        logger.error(f"Error fetching history for node {node_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching history")
