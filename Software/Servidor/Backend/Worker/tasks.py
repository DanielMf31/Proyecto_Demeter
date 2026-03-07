import sys
import os
import json
import uuid
import time
import shutil
import pandas as pd
from datetime import datetime, timedelta
import asyncio

# Configurar path para importar desde 'Backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Core.database import AsyncSessionLocal
from Core.redis import redis_manager
from BD.models import TelemetryAmbient, Plant
from sqlalchemy.future import select
from Analisis_datos.calculos_agronomicos import procesar_dataframe
from Analisis_datos.generar_graficas import procesar_graficas_generales
import logging

logger = logging.getLogger("worker_tasks")
logging.basicConfig(level=logging.INFO)

async def _async_export_experiment_data(experimento_id: int, ref_date_str: str, days: int) -> str:
    """
    Motor ETL Complejo de Exportación ejecutado en Background (RQ Worker).
    
    1. Extrae datos crudos (desde Redis o fallback a PostgreSQL).
    2. Transforma la serie temporal usando Pandas (Calcula VPD, GDD, Entalpía, Z-Scores).
    3. Carga los resultados en Redis para lectura ultrarrápida (dashboard temporal).
    4. Serializa gráficos y genera excels diarios por planta.
    5. Empaqueta un ZIP que luego puede descargar el usuario.
    
    :param experimento_id: ID Relacional del Experimento.
    :param ref_date_str: Fecha ancla límite de extracción (ISO 8601).
    :param days: Ventana retrospectiva de días a calcular (típicamente 30).
    :return: Ruta en disco del ZIP temporal generado.
    """
    logger.info(f"Iniciando Exportación ETL para Experimento {experimento_id}, Días: {days}")
    start_time = time.time()
    
    await redis_manager.connect()
    
    # Parsear fecha de referencia
    # Espera formato ISO como "2026-02-21T00:00:00"
    if "T" not in ref_date_str:
        ref_date_str += "T23:59:59"
    ref_date = datetime.fromisoformat(ref_date_str.replace("Z", "+00:00")).replace(tzinfo=None)
    start_date = ref_date - timedelta(days=days)
    
    # 1. Extracción de Redis
    cache_key = f"demeter:raw_data:experimento_{experimento_id}"
    raw_data_str = None
    if redis_manager.redis:
        raw_data_str = await redis_manager.redis.get(cache_key)
        
    raw_data = []
    if raw_data_str:
        logger.info("Caché HIT: Cargando desde Redis.")
        all_data = json.loads(raw_data_str)
        # Filtrar fechas
        for row in all_data:
            ts = datetime.fromisoformat(row["timestamp"])
            if start_date <= ts <= ref_date:
                raw_data.append(row)
    else:
        logger.warning("Caché MISS: Haciendo fallback a PostgreSQL.")
        async with AsyncSessionLocal() as session:
            # Obtener plantas del experimento
            result = await session.execute(select(Plant).where(Plant.experiment_id == experimento_id))
            plants = result.scalars().all()
            plant_node_ids = [p.node_id for p in plants]
            
            if plant_node_ids:
                from sqlalchemy import and_
                tl_result = await session.execute(
                    select(TelemetryAmbient).where(
                        and_(
                            TelemetryAmbient.node_id.in_(plant_node_ids),
                            TelemetryAmbient.timestamp >= start_date,
                            TelemetryAmbient.timestamp <= ref_date
                        )
                    )
                )
                db_data = tl_result.scalars().all()
                for rec in db_data:
                    raw_data.append({
                        "timestamp": rec.timestamp.isoformat(),
                        "node_id": rec.node_id,
                        "temperature": rec.air_temperature,
                        "humidity": rec.air_humidity
                    })
    
    if not raw_data:
        raise ValueError("No se encontraron datos para los criterios especificados.")

    logger.info(f"Extracción completada. Registros a transformar: {len(raw_data)}")
    
    # 2. Transformación (DataFrame y Cálculos)
    df_crudo = pd.DataFrame(raw_data)
    df_crudo["timestamp"] = pd.to_datetime(df_crudo["timestamp"])
    
    datos_nodos = {}
    calculated_results_for_redis = {}
    
    for node_id, df_planta in df_crudo.groupby("node_id"):
        try:
            # procesar_dataframe calcula VPD, medias móviles, etc.
            df_horario, _ = procesar_dataframe(df_planta)
            # Para que json.dumps funcione con las fechas:
            df_horario_dict = df_horario.to_dict(orient="records")
            # Corregir los NaNs a None para que json.dumps no falle
            for record in df_horario_dict:
                for k, v in record.items():
                    if pd.isna(v):
                        record[k] = None

            datos_nodos[str(node_id)] = df_horario
            calculated_results_for_redis[str(node_id)] = df_horario_dict
            
        except Exception as e:
            logger.error(f"Error procesando nodo {node_id}: {e}")
            pass
            
    # 3. Caché de Resultados (Todo lo calculado a Redis)
    if redis_manager.redis and calculated_results_for_redis:
        calc_key = f"demeter:calculated_data:experimento_{experimento_id}"
        # TTL 30 dias = 2592000 segs
        await redis_manager.redis.setex(calc_key, 2592000, json.dumps(calculated_results_for_redis, default=str))
        logger.info(f"Resultados calculados cacheados en Redis ({calc_key}).")

    # 4. Generar Carpetas y ZIP agrupado por DÍA
    export_id = str(uuid.uuid4())[:8]
    base_export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'exports'))
    os.makedirs(base_export_dir, exist_ok=True)
    
    zip_root = os.path.join(base_export_dir, f"export_temp_{export_id}")
    exp_dir = os.path.join(zip_root, f"Experimento_{experimento_id}")
    os.makedirs(exp_dir, exist_ok=True)
    
    # Identificar todos los días presentes en los datos
    dias_unicos = set()
    for node_id, df_hor in datos_nodos.items():
        if "Timestamp" in df_hor.columns:
            # Crear columna auxiliar para filtrar
            df_hor["Date"] = df_hor["Timestamp"].dt.date
            dias_unicos.update(df_hor["Date"].unique())

    # Generar reportes día por día
    for day in sorted(list(dias_unicos)):
        day_str = day.strftime("%Y-%m-%d")
        day_dir = os.path.join(exp_dir, day_str)
        os.makedirs(day_dir, exist_ok=True)
        
        # Extraer sólo los datos correspondientes a este día
        datos_dia = {}
        for node_id, df_hor in datos_nodos.items():
            if "Date" in df_hor.columns:
                df_dia = df_hor[df_hor["Date"] == day].copy()
                if not df_dia.empty:
                    datos_dia[node_id] = df_dia
                    
        if datos_dia:
            # Gráficas exclusivas de este día
            procesar_graficas_generales(datos_dia, day_dir)
            
            # Excel exclusivo de este día
            for node_id, df_dia in datos_dia.items():
                planta_dir = os.path.join(day_dir, f"Planta_{node_id}")
                os.makedirs(planta_dir, exist_ok=True)
                
                # Limpieza antes de exportar
                if "Timestamp" in df_dia.columns:
                    df_dia["Timestamp"] = df_dia["Timestamp"].dt.tz_localize(None)
                if "Date" in df_dia.columns:
                    df_dia = df_dia.drop(columns=["Date"])
                    
                excel_path = os.path.join(planta_dir, f"datos_calculados_planta_{node_id}.xlsx")
                with pd.ExcelWriter(excel_path) as writer:
                    df_dia.to_excel(writer, sheet_name="Telemetria_Completa", index=False)
            
    # Empaquetar en ZIP
    zip_root = os.path.join(base_export_dir, f"export_temp_{export_id}")
    zip_path_no_ext = os.path.join(base_export_dir, f"reporte_exp_{experimento_id}_{export_id}")
    
    shutil.make_archive(zip_path_no_ext, 'zip', root_dir=zip_root)
    
    # Limpiar temp dir
    shutil.rmtree(zip_root)
    zip_file = f"{zip_path_no_ext}.zip"
    
    if redis_manager.redis:
        await redis_manager.close()
        
    end_time = time.time()
    elapsed = round(end_time - start_time, 2)
    logger.info(f"Exportación de {days} días finalizada en {elapsed} segundos. Archivo ZIP creado.")
    
    # Retorna SOLO la ruta del arhivo para que FileResponse() funcione de inmediato
    return zip_file

def export_experiment_data(experimento_id: int, ref_date_str: str, days: int) -> str:
    """
    Función síncrona entry-point para RQ.
    """
    return asyncio.run(_async_export_experiment_data(experimento_id, ref_date_str, days))
