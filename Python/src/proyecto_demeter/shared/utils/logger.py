import logging
import sys
from pathlib import Path
from proyecto_demeter.shared.config.provider import settings

def setup_logger(name: str = "TicketProcessor") -> logging.Logger:
    """
    Configura y devuelve un logger estandarizado.
    """
    logger = logging.getLogger(name)
    
    # Si ya tiene handlers, no añadir más (evita duplicados)
    if logger.handlers:
        return logger
        
    logger.setLevel(settings.log_level)
    
    # Formato
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (opcional, si existe directorio de logs)
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

def generate_crash_report(state: dict, error: Exception, step_name: str = "unknown") -> str:
    """
    Genera un informe detallado del error (Crash Report) en JSON.
    Guarda el archivo en `logs/crashes/` y devuelve la ruta del archivo.
    """
    import json
    import traceback
    from datetime import datetime
    
    # 1. Preparar Directorio
    crash_dir = Path("logs/crashes")
    crash_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Construir Nombre de Archivo
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crash_{timestamp_str}_{step_name}.json"
    filepath = crash_dir / filename
    
    # 3. Serializar Estado (Manejo de objetos no serializables)
    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""
        if hasattr(obj, 'model_dump'):
            return obj.model_dump()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    # 4. Crear Payload
    report = {
        "timestamp": datetime.now().isoformat(),
        "step": step_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "stack_trace": traceback.format_exc(),
        "state_dump": state
    }
    
    # 5. Guardar
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, default=json_serial, ensure_ascii=False)
        return str(filepath)
    except Exception as e:
        # Fallback si falla el guardado del reporte
        fallback_msg = f"CRITICAL: Failed to save crash report: {e}"
        print(fallback_msg)
        return ""
