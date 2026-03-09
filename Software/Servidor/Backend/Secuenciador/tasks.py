import sys
import os
import json
import logging
from datetime import datetime, timedelta, timezone
import numpy as np

# Configurar path para importar módulos de Backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core.database import AsyncSessionLocal
from Core.redis import redis_manager
from BD.models import TelemetryAmbient, Plant, Experiment
from sqlalchemy.future import select
from redis import Redis
from rq import Queue
from Core.config import get_settings

logger = logging.getLogger("sec_tasks")

async def sync_sensor_data_to_redis():
    """
    Sincroniza los últimos 24 horas de datos de sensores (TelemetryAmbient)
    desde PostgreSQL principal hacia la memoria caché rápida en Redis.
    
    Permite absorber ráfagas de lectura del Frontend sin saturar la Base de Datos.
    
    Nota de diseño: El caché particiona los datos por ID de Experimento
    (ej: "demeter:raw_data:experimento_1") facilitando el acceso O(1).
    """
    logger.info("Secuenciador: Iniciando Sync PostgreSQL -> Redis (Últimas 24h)...")
    await redis_manager.connect()
    outdated_date = datetime.utcnow() - timedelta(days=1)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Experiment))
        experiments = result.scalars().all()
        for exp in experiments:
            plants_res = await session.execute(select(Plant).where(Plant.experiment_id == exp.id))
            plants = plants_res.scalars().all()
            node_ids = [p.node_id for p in plants]
            if not node_ids:
                continue
                
            from sqlalchemy import and_
            tl_res = await session.execute(
                select(TelemetryAmbient).where(
                    and_(
                        TelemetryAmbient.node_id.in_(node_ids),
                        TelemetryAmbient.timestamp >= outdated_date
                    )
                )
            )
            db_data = tl_res.scalars().all()
            raw_data = []
            for rec in db_data:
                raw_data.append({
                    "timestamp": rec.timestamp.isoformat(),
                    "node_id": rec.node_id,
                    "temperature": rec.air_temperature,
                    "humidity": rec.air_humidity
                })
            
            # Siempre se añade, aunque esté vacío, para limpiar data antigua
            if redis_manager.redis:
                cache_key = f"demeter:raw_data:experimento_{exp.id}"
                await redis_manager.redis.set(cache_key, json.dumps(raw_data))
                logger.info(f"Sync completado Exp {exp.id}: {len(raw_data)} registros cacheados.")
                
    if redis_manager.redis:
        await redis_manager.close()

async def dummy_insert_test_data():
    """
    Función de testeo (DEMO). Simula tráfico entrante M2M generando registros aleatorios 
    de temperatura y humedad para todas las plantas (Node IDs) activas en el sistema,
    insertándolos en la BD y recargando el caché.
    
    Debería deshabilitarse o eliminarse en el despliegue a Producción (PROD).
    """
    logger.info("Secuenciador: Job Dummy (TEST_DATA) insertando registros aleatorios actuales...")
    now = datetime.utcnow()
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Plant))
        plants = result.scalars().all()
        
        records = []
        for p in plants:
            # Temp 20-25, HR 50-70
            t = round(20 + np.random.random() * 5, 2)
            h = round(50 + np.random.random() * 20, 2)
            
            records.append(TelemetryAmbient(
                timestamp=now,
                node_id=p.node_id,
                temperature=t,
                humidity=h
            ))
            
        if records:
            session.add_all(records)
            await session.commit()
            logger.info(f"Se insertaron {len(records)} registros dummy.")
    
    # Forzamos sincronización del caché
    await sync_sensor_data_to_redis()

async def enqueue_nightly_etl():
    """
    Programa vía RQ (Redis Queue) la tarea pesada nocturna de Extracción, 
    Transformación y Carga (ETL). Extrae 30 días móviles de historial,
    computa cálculos agronómicos masivos en paralelo y guarda perfiles CSV limpios.
    
    Esta función NO procesa en sí, únicamente hace "trigger" al pool de Workers de RQ 
    para liberar el hilo del Secuenciador de inmediato.
    """
    logger.info("Secuenciador: Iniciando Trigger Nocturno de Cálculos ETL en Worker...")
    settings = get_settings()
    redis_url = getattr(settings, "RQ_REDIS_URL", "redis://redis:6379/1")
    redis_conn = Redis.from_url(redis_url)
    task_queue = Queue("demeter_tasks", connection=redis_conn)
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Experiment))
        experiments = result.scalars().all()
        
        now_str = datetime.utcnow().isoformat()
        for exp in experiments:
            job_id = f"nightly_{exp.id}_{now_str[:10]}"
            try:
                job = task_queue.enqueue(
                    "Worker.tasks.export_experiment_data", 
                    exp.id,
                    now_str,
                    30, # default 30 days history calculated
                    job_id=job_id,
                    job_timeout='20m'
                )
                logger.info(f"Encolado ETL Nightly. Exp: {exp.id}, JobID: {job.get_id()}")
            except Exception as e:
                logger.error(f"Fallo al encolar tarea nocturna: {e}")
