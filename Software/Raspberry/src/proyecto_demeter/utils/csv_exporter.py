import csv
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from configuration import settings


class CsvExporter:
    """
    Daily CSV telemetry exporter with automatic rotation and retention.
    Files: telemetry_YYYY-MM-DD.csv in the configured data directory.
    """

    def __init__(self, csv_dir: str = None):
        self.csv_dir = csv_dir or str(Path(settings.BASE_DIR) / "data" / "csv")
        self.logger = logging.getLogger("CsvExporter")
        os.makedirs(self.csv_dir, exist_ok=True)
        self._headers = [
            "timestamp", "type", "node_id", "plant_id",
            "temperature", "humidity", "soil_temperature", "soil_moisture",
        ]

    def _get_path(self, date: datetime = None) -> str:
        if date is None:
            date = datetime.now()
        filename = f"telemetry_{date.strftime('%Y-%m-%d')}.csv"
        return os.path.join(self.csv_dir, filename)

    def write_row(self, row: dict) -> None:
        """Append a single telemetry row to today's CSV file."""
        path = self._get_path()
        write_header = not os.path.exists(path)
        try:
            with open(path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self._headers, extrasaction="ignore")
                if write_header:
                    writer.writeheader()
                writer.writerow(row)
        except Exception as e:
            self.logger.error(f"CSV write error: {e}")

    def cleanup(self, retention_days: int = 7) -> None:
        """Remove CSV files older than retention_days."""
        cutoff = datetime.now() - timedelta(days=retention_days)
        try:
            for fname in os.listdir(self.csv_dir):
                if not fname.startswith("telemetry_") or not fname.endswith(".csv"):
                    continue
                # Parse date from filename
                date_str = fname[len("telemetry_"):-len(".csv")]
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
                if file_date < cutoff:
                    os.remove(os.path.join(self.csv_dir, fname))
                    self.logger.info(f"Removed old CSV: {fname}")
        except Exception as e:
            self.logger.error(f"CSV cleanup error: {e}")
