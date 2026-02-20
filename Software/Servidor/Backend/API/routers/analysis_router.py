import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel
from rq import Queue
from redis import Redis
from Core.config import get_settings

router = APIRouter()
settings = get_settings()

# Inicializamos la conexión a Redis síncrona para RQ
# RQ requiere una conexión síncrona, a diferencia de redis.asyncio
# IMPORTANTE: Asumimos que la URL es redis://redis:6379/0 por defecto en docker
redis_conn = Redis.from_url(settings.REDIS_URL or "redis://redis:6379/0")
task_queue = Queue("demeter_tasks", connection=redis_conn)

class AnalysisRequest(BaseModel):
    experimento_id: int

@router.post("/generate")
async def generate_analysis(request: AnalysisRequest):
    """
    Encola una tarea pesada de análisis científico en el background worker (RQ).
    Devuelve el ID de la tarea para que el cliente pueda consultar su estado.
    """
    try:
        # Encolamos la tarea en RQ
        # Se le pasa el nombre de la función como string para evitar problemas de importación
        # Si tasks.py está en el mismo nivel, se puede importar, pero como string funciona bien.
        job = task_queue.enqueue(
            "tasks.generar_analisis_cientifico", 
            request.experimento_id,
            job_timeout=600 # 10 minutos de timeout
        )
        return {
            "status": "processing",
            "task_id": job.id,
            "message": "Task enqueued successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_analysis_status(task_id: str):
    """
    Consulta el estado de una tarea en RQ.
    Estados posibles: queued, started, finished, failed, canceled
    """
    try:
        job = task_queue.fetch_job(task_id)
        if not job:
            raise HTTPException(status_code=404, detail="Task not found")
        
        response = {
            "status": job.get_status(),
            "task_id": job.id,
        }
        
        if job.is_finished:
            # Result contiene el diccionario devuelto por la tarea: {"filename": "..."}
            response["result"] = job.result
        elif job.is_failed:
            response["error"] = str(job.exc_info)
            
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_analysis(filename: str):
    """
    Descarga el archivo generado por el worker desde el volumen compartido.
    """
    # Evitar path traversal
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    file_path = os.path.join("/app/shared", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not ready or not found")
        
    return FileResponse(
        path=file_path, 
        media_type="application/zip", 
        filename=filename
    )
