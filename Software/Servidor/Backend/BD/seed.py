import asyncio
import logging
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from Core.database import AsyncSessionLocal
from BD.models import TelemetryTH

logger = logging.getLogger("seed")
logging.basicConfig(level=logging.INFO)

async def seed_test_data(db: AsyncSession):
    """
    Inyecta datos de prueba en la BD (10 nodos, 24 mediciones cada uno).
    Genera datos estables (senoidales) para 'Ayer' de 00:00 a 23:00.
    Elimina datos de prueba anteriores para asegurar un entorno limpio.
    """
    logger.info("Limpiando datos de prueba anteriores en TelemetryTH (Nodos 1-10)...")
    
    # Delete previous test data for nodes 1-10 to always have fresh exactly 24h data
    from sqlalchemy import delete
    await db.execute(delete(TelemetryTH).where(TelemetryTH.node_id.in_(range(1, 11))))
    await db.commit()

    logger.info("Iniciando inyección de datos de prueba para 'Ayer' (00:00 - 23:00)...")
    
    # Calcular fecha base: "Ayer" a las 00:00
    now = datetime.utcnow()
    yesterday_base = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    
    new_records = []
    import math
    
    for node_id in range(1, 11):
        # Ajustes ligeros por nodo para que no sean idénticos
        t_base = 22.0 + (node_id * 0.2 - 1.0)
        h_base = 60.0 + (node_id * 1.5 - 7.5)
        
        for hour in range(24):
            timestamp = yesterday_base + timedelta(hours=hour)
            
            # Onda senoidal simple: min temperatura a las 4 AM, max a las 14 PM
            # phase shift para que el minimo este en la hora 4
            t_offset = math.cos((hour - 14) * math.pi / 12) * -5.0 # Amplitud de 5C (min 17, max 27)
            temperature = round(t_base - t_offset, 2)
            
            # Humedad inversamente proporcional a la temperatura
            # Max humedad a las 4 AM, min a las 14 PM
            h_offset = math.cos((hour - 4) * math.pi / 12) * -20.0 # Amplitud de 20%
            humidity = round(h_base - h_offset, 2)
            
            # Asegurar limites
            humidity = max(10.0, min(100.0, humidity))
            
            record = TelemetryTH(
                timestamp=timestamp,
                node_id=node_id,
                temperature=temperature,
                humidity=humidity
            )
            new_records.append(record)
            
    db.add_all(new_records)
    await db.commit()
    logger.info(f"Seeding completado. {len(new_records)} registros insertados para el día {yesterday_base.date()}.")

async def main():
    async with AsyncSessionLocal() as session:
        await seed_test_data(session)

if __name__ == "__main__":
    asyncio.run(main())
