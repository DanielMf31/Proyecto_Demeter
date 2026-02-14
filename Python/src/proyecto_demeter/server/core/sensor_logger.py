import logging
import csv
import os
import time
from datetime import datetime
from ..config.schemas import DataReport

class SensorLogger:
    """
    Logs sensor data to a CSV file.
    """
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "sensor_data.csv")
        self._ensure_header()

    def _ensure_header(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Epoch", "NodeID", "Temperature", "Humidity"])

    def log_report(self, report: DataReport):
        """Append a DataReport to the CSV log."""
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
        epoch = time.time()
        
        with open(self.log_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp_str, 
                f"{epoch:.2f}", 
                report.node_id, 
                f"{report.temperature:.2f}", 
                f"{report.humidity:.2f}"
            ])
            
        logging.info(f"SensorLogger: Saved data for Node {report.node_id}")
