
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from config.config import config

class SystemLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemLogger, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def setup(self):
        if self.initialized:
            return

        # 1. Crear directorios
        os.makedirs(config.SESSION_LOG_DIR, exist_ok=True)

        # 2. Nombre de archivo de sesión
        session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        log_file = config.SESSION_LOG_DIR / f"{session_id}.log"

        # 3. Configurar Root Logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG) # Capturar todo

        # Formato estándar
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-15s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # 4. Handler: Archivo (DEBUG+)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 5. Handler: Consola (INFO+)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Mensaje inicial
        logging.getLogger("System").info(f"=== INICIO DE SESIÓN: {session_id} ===")
        logging.getLogger("System").info(f"Log guardado en: {log_file}")

        self.initialized = True

    @staticmethod
    def get_logger(name):
        return logging.getLogger(name)

# Instancia global
sys_logger = SystemLogger()
