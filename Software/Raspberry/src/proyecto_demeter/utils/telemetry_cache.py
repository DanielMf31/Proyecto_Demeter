import logging
from datetime import datetime

from schemas import DemeterCommand, TempHumReport, SensorClusterReport
from proyecto_demeter.utils.database import DatabaseManager
from proyecto_demeter.utils.csv_exporter import CsvExporter


class TelemetryCacheManager:
    """
    Store-and-forward cache that wraps DatabaseManager + CsvExporter.
    - Caches all incoming telemetry locally (SQLite + CSV).
    - Replays unsynced rows when WebSocket reconnects.
    """

    def __init__(self):
        self.logger = logging.getLogger("TelemetryCacheManager")
        self.db = DatabaseManager()
        self.csv = CsvExporter()

    async def cache_command(self, cmd: DemeterCommand) -> None:
        """Cache a telemetry command to SQLite and CSV."""
        now = datetime.now()

        if isinstance(cmd, TempHumReport):
            await self.db.save_reading(
                node_id=cmd.node_id,
                temperature=cmd.temperature,
                humidity=cmd.humidity,
                timestamp=now,
            )
            self.csv.write_row({
                "timestamp": now.isoformat(),
                "type": "ambient",
                "node_id": cmd.node_id,
                "temperature": cmd.temperature,
                "humidity": cmd.humidity,
            })

        elif isinstance(cmd, SensorClusterReport):
            for entry in cmd.entries:
                await self.db.save_cluster_reading(
                    plant_id=entry.plant_id,
                    soil_temperature=entry.temperature,
                    soil_moisture=entry.soil_moisture,
                    timestamp=now,
                )
                self.csv.write_row({
                    "timestamp": now.isoformat(),
                    "type": "soil",
                    "node_id": cmd.node_id,
                    "plant_id": entry.plant_id,
                    "soil_temperature": entry.temperature,
                    "soil_moisture": entry.soil_moisture,
                })

    async def replay_unsynced(self, ws_client) -> None:
        """
        Replay all unsynced telemetry rows to the backend via WebSocket.
        Called on WS reconnect.
        """
        # Replay ambient readings
        ambient_rows = await self.db.get_unsynced("sensor_readings")
        if ambient_rows:
            self.logger.info(f"Replaying {len(ambient_rows)} unsynced ambient readings")
            synced_ids = []
            for row in ambient_rows:
                payload = {
                    "type": "temp_hum_report",
                    "target_id": 0,
                    "node_id": row["node_id"],
                    "temperature": row["temperature"],
                    "humidity": row["humidity"],
                    "timestamp": 0.0,
                }
                try:
                    await ws_client.send_json(payload)
                    synced_ids.append(row["id"])
                except Exception as e:
                    self.logger.error(f"Replay ambient failed: {e}")
                    break
            await self.db.mark_synced("sensor_readings", synced_ids)

        # Replay soil readings
        soil_rows = await self.db.get_unsynced("soil_readings")
        if soil_rows:
            self.logger.info(f"Replaying {len(soil_rows)} unsynced soil readings")
            synced_ids = []
            for row in soil_rows:
                payload = {
                    "type": "sensor_cluster_report",
                    "target_id": 0,
                    "node_id": 0,
                    "entries": [{
                        "plant_id": row["plant_id"],
                        "temperature": row["soil_temperature"],
                        "soil_moisture": row["soil_moisture"],
                    }],
                }
                try:
                    await ws_client.send_json(payload)
                    synced_ids.append(row["id"])
                except Exception as e:
                    self.logger.error(f"Replay soil failed: {e}")
                    break
            await self.db.mark_synced("soil_readings", synced_ids)

        # Clean up old synced data
        await self.db.cleanup_old(days=30)
        self.csv.cleanup(retention_days=7)
