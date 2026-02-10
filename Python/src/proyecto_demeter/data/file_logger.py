import logging
import logging.handlers
import os
from ..config import settings

class SensorLogger:
    """
    Handles logging of sensor data to a separate file.
    Format: CSV
    """
    def __init__(self, log_dir: str = None, filename: str = None):
        self.log_dir = log_dir if log_dir else str(settings.LOG_DIR)
        self.filename = filename if filename else "sensors.log" # Assuming filename default is not from settings based on snippet
        self.filepath = os.path.join(self.log_dir, self.filename)
        
        # Ensure directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure specific logger
        self.logger = logging.getLogger("demeter_sensors")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False # Do not propagate to root logger (avoid console spam)
        
        # File Handler with Rotation (10MB, 5 backups)
        handler = logging.handlers.RotatingFileHandler(
            self.filepath, maxBytes=10*1024*1024, backupCount=5
        )
        
        # CSV Format: ISO_TIMESTAMP,NODE_ID,TEMP,HUM
        formatter = logging.Formatter('%(asctime)s,%(message)s')
        handler.setFormatter(formatter)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def log_reading(self, node_id: int, temperature: float, humidity: float):
        """
        Logs a sensor reading in CSV format.
        Timestamp is added automatically by formatter.
        """
        # Message: NODE_ID,TEMP,HUM
        self.logger.info(f"{node_id},{temperature:.2f},{humidity:.2f}")

    def get_log_path(self) -> str:
        return self.filepath
