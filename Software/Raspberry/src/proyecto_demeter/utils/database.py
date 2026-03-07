import aiosqlite
import logging
from datetime import datetime, timedelta
# Import Common Configuration
from configuration import settings


class DatabaseManager:
    """
    Manages SQLite database storage for sensor data.
    Uses async IO to interact with the DB.
    """
    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path else settings.DB_PATH
        self.logger = logging.getLogger("DatabaseManager")

    async def init_db(self):
        """Initializes the database schema with migration support."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Original ambient readings table
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        node_id INTEGER NOT NULL,
                        temperature REAL,
                        humidity REAL,
                        synced INTEGER DEFAULT 0
                    )
                """)
                # Soil readings table (from sensor cluster reports)
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS soil_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        plant_id INTEGER NOT NULL,
                        soil_temperature REAL,
                        soil_moisture REAL,
                        synced INTEGER DEFAULT 0
                    )
                """)
                # Indexes
                await db.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_node ON sensor_readings(node_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_sr_synced ON sensor_readings(synced)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_soil_timestamp ON soil_readings(timestamp)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_soil_plant ON soil_readings(plant_id)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_soil_synced ON soil_readings(synced)")

                # Migration: add synced column to sensor_readings if missing
                cursor = await db.execute("PRAGMA table_info(sensor_readings)")
                columns = [row[1] for row in await cursor.fetchall()]
                if "synced" not in columns:
                    await db.execute("ALTER TABLE sensor_readings ADD COLUMN synced INTEGER DEFAULT 0")

                await db.commit()
                self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to init DB: {e}")

    async def save_reading(self, node_id: int, temperature: float, humidity: float, timestamp: datetime = None):
        """Saves an ambient sensor reading."""
        if timestamp is None:
            timestamp = datetime.now()

        ts_str = timestamp.isoformat()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO sensor_readings (timestamp, node_id, temperature, humidity, synced) VALUES (?, ?, ?, ?, 0)",
                    (ts_str, node_id, temperature, humidity)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save reading: {e}")

    async def save_cluster_reading(self, plant_id: int, soil_temperature: float, soil_moisture: float, timestamp: datetime = None):
        """Saves a soil sensor reading from a cluster report."""
        if timestamp is None:
            timestamp = datetime.now()

        ts_str = timestamp.isoformat()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO soil_readings (timestamp, plant_id, soil_temperature, soil_moisture, synced) VALUES (?, ?, ?, ?, 0)",
                    (ts_str, plant_id, soil_temperature, soil_moisture)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save cluster reading: {e}")

    async def get_unsynced(self, table: str = "sensor_readings", limit: int = 500) -> list:
        """Retrieves unsynced rows from the specified table."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    f"SELECT * FROM {table} WHERE synced = 0 ORDER BY timestamp ASC LIMIT ?",
                    (limit,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error fetching unsynced from {table}: {e}")
            return []

    async def mark_synced(self, table: str, ids: list[int]):
        """Marks rows as synced by their IDs."""
        if not ids:
            return
        try:
            placeholders = ",".join("?" for _ in ids)
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"UPDATE {table} SET synced = 1 WHERE id IN ({placeholders})",
                    ids
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Error marking synced in {table}: {e}")

    async def cleanup_old(self, days: int = 30):
        """Removes synced rows older than the specified number of days."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                for table in ("sensor_readings", "soil_readings"):
                    await db.execute(
                        f"DELETE FROM {table} WHERE synced = 1 AND timestamp < ?",
                        (cutoff,)
                    )
                await db.commit()
                self.logger.info(f"Cleaned up synced rows older than {days} days")
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")

    async def get_stats(self, node_id: int, hours: int = 24) -> dict:
        """
        Retrieves statistics (Avg, Min, Max) for a node in the last N hours.
        """
        start_time = datetime.now() - timedelta(hours=hours)

        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute(
                    """
                    SELECT
                        AVG(temperature) as avg_temp,
                        MIN(temperature) as min_temp,
                        MAX(temperature) as max_temp,
                        AVG(humidity) as avg_hum
                    FROM sensor_readings
                    WHERE node_id = ? AND timestamp >= ?
                    """,
                    (node_id, start_time.isoformat())
                ) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return {
                            "avg_temp": row[0],
                            "min_temp": row[1],
                            "max_temp": row[2],
                            "avg_hum": row[3]
                        }
                    return {}
        except Exception as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {}

    async def get_recent_readings(self, limit: int = 10) -> list:
        """Retrieves the most recent readings."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(
                    "SELECT * FROM sensor_readings ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                ) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error fetching recent readings: {e}")
            return []
