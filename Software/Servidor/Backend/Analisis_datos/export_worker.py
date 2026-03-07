import os
import shutil
import tempfile
import asyncio
from datetime import datetime, timedelta, timezone
import pandas as pd
from sqlalchemy.future import select

# This is necessary because RQ jobs don't run inside the FastAPI process,
# they run in a detached process, so we need to initialize DB connections
from Core.database import AsyncSessionLocal
from BD.models import TelemetryAmbient

# Import new refined analysis modules
from Analisis_datos.calculos_agronomicos import procesar_dataframe
from Analisis_datos.generar_graficas import procesar_graficas_generales

async def _extract_data(job_id: str):
    """
    Async extraction logic inside the sync RQ job shell.
    Includes caching for yesterday's data.
    """
    # 1. Prepare Export Directory (in the shared docker volume /app/exports)
    base_export_dir = os.environ.get("EXPORT_DATA_DIR", "/app/exports")
    if not os.path.exists(base_export_dir):
        base_export_dir = tempfile.gettempdir()
        
    cache_dir = os.path.join(base_export_dir, "permanente")
    os.makedirs(cache_dir, exist_ok=True)
    
    # Check CACHE for "Yesterday"
    now = datetime.now(timezone.utc)
    yesterday = now.date() - timedelta(days=1)
    # The cache assumes we always requested "yesterday" from 00:00 to 23:59.
    cached_zip_name = f"Exportacion_Agronomica_{yesterday.isoformat()}.zip"
    cached_zip_path = os.path.join(cache_dir, cached_zip_name)
    
    if os.path.exists(cached_zip_path):
        import logging
        logging.getLogger("worker").info(f"Serving cached export: {cached_zip_path}")
        return cached_zip_path
        
    # If not cached, proceed with generation.
    export_folder = os.path.join(base_export_dir, f"Exportacion_Temporal_{job_id}")
    comparacion_folder = os.path.join(export_folder, "Comparacion_Global")
    os.makedirs(comparacion_folder, exist_ok=True)
    
    # Calculate exactly yesterday boundaries
    start_of_yesterday = datetime.combine(yesterday, datetime.min.time())
    end_of_yesterday = start_of_yesterday + timedelta(days=1, microseconds=-1)
    
    # 2. Fetch data from Database
    async with AsyncSessionLocal() as session:
        # Fetch records between start and end of yesterday
        query = select(TelemetryAmbient).where(
            TelemetryAmbient.node_id.in_(range(1, 11)),
            TelemetryAmbient.timestamp >= start_of_yesterday,
            TelemetryAmbient.timestamp <= end_of_yesterday
        )
        result = await session.execute(query)
        records = result.scalars().all()
        
        if not records:
            raise ValueError(f"No telemetry data found for {yesterday.isoformat()} in job {job_id}")
            
        data = [{
            "timestamp": r.timestamp,
            "node_id": r.node_id,
            "temperature": r.air_temperature,
            "humidity": r.air_humidity
        } for r in records]
        
    # 3. Process with Pandas and Agronomic Module
    df_crudo = pd.DataFrame(data)
    nodes = df_crudo["node_id"].unique()
    
    # Diccionario para almacenar el df_horario procesado de cada nodo para pasarlo a generar_graficas
    datos_nodos_procesados = {}
    
    with pd.ExcelWriter(os.path.join(comparacion_folder, "Calculos_Agronomicos_Global.xlsx")) as writer:
        for node in nodes:
            node_folder = os.path.join(export_folder, f"Planta_{node}")
            os.makedirs(node_folder, exist_ok=True)
            
            # Filtramos el crudo por nodo
            df_node_crudo = df_crudo[df_crudo["node_id"] == node]
            
            # Pasamos a la librería matemática (limpia de radiación solar)
            df_horario, df_resumen = procesar_dataframe(df_node_crudo)
            
            if not df_horario.empty:
                datos_nodos_procesados[str(node)] = df_horario
                
                # Excel Individual "Planta X"
                node_excel = os.path.join(node_folder, f"Datos_Agro_Planta_{node}.xlsx")
                with pd.ExcelWriter(node_excel) as node_writer:
                    df_horario.to_excel(node_writer, sheet_name="Series_Horarias", index=False)
                    df_resumen.to_excel(node_writer, sheet_name="Resumen_Métricas", index=False)
                
                # Aprovechar y meter al Excel Global como una hoja más para facilitar cruces
                sheet_name = f"Planta_{node}"[:31]
                df_horario.to_excel(writer, sheet_name=sheet_name, index=False)
    
    # 4. Generar Gráficos usando Seaborn (Comparativas e individuales agrupadas juntas)
    # Le delegamos el df diccionario procesado `datos_nodos_procesados`
    if datos_nodos_procesados:
        procesar_graficas_generales(datos_nodos_procesados, export_folder)
        
    # 5. Compress the folder and move to Cache (permanente)
    zip_path_base_temp = os.path.join(base_export_dir, f"temp_{job_id}")
    shutil.make_archive(zip_path_base_temp, 'zip', export_folder)
    
    # Move the created archive to its final cached destination
    shutil.move(f"{zip_path_base_temp}.zip", cached_zip_path)
    
    # Cleanup temporal raw folder
    shutil.rmtree(export_folder)
    
    # Return the path to the cached zip file
    return cached_zip_path

def generate_export_bundle(job_id: str):
    """
    Main entry point for the RQ worker.
    Runs the async logic in a synchronous wrapper since RQ defaults to sync functions.
    """
    return asyncio.run(_extract_data(job_id))
