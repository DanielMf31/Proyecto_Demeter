
import json
import os
from pathlib import Path

class Config:
    # Constantes
    BASE_DIR = Path(__file__).parent.parent
    LOG_DIR = BASE_DIR / "logs"
    SESSION_LOG_DIR = LOG_DIR / "sessions"
    SETTINGS_FILE = BASE_DIR / "config" / "settings.json"
    
    # Defaults
    DEFAULT_PORT = '/dev/serial0'
    DEFAULT_BAUDRATE = 115200
    
    def __init__(self):
        self.port = self.DEFAULT_PORT
        self.baudrate = self.DEFAULT_BAUDRATE
        self.load()

    def load(self):
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    data = json.load(f)
                    uart_cfg = data.get('uart', {})
                    self.port = uart_cfg.get('port', self.DEFAULT_PORT)
                    self.baudrate = uart_cfg.get('baudrate', self.DEFAULT_BAUDRATE)
            except Exception as e:
                print(f"[Config] Error cargando settings.json: {e}")
        else:
            print("[Config] Archivo settings.json no encontrado, usar defaults.")

# Singleton instance
config = Config()
