import logging
import sys
from .config import get_settings

settings = get_settings()

def setup_logger(name: str = __name__):
    """
    Genera una instancia estándar del formateador de logs de Python para todo el backend.
    
    :param name: Nombre del logger (ej: "app" o "ws_dispatcher").
    :return: Objeto Logger configurado con DEBUG/INFO condicional.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
