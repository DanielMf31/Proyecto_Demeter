import aiosqlite
import logging
from datetime import datetime, timedelta
from ..config import settings

class DatabaseManager:
    """
    Manages SQLite database storage for sensor data.
    Uses async IO to interact with the DB.
    """
    def __init__(self, db_path: str = None):
        self.db_path = db_path if db_path else settings.DB_PATH
        self.logger = logging.getLogger("DatabaseManager")

    async def init_db(self):
        """Initializes the database schema."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sensor_readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        node_id INTEGER NOT NULL,
                        temperature REAL,
                        humidity REAL
                    )
                """)
                # Indexes for performance
                await db.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON sensor_readings(timestamp)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_node ON sensor_readings(node_id)")
                await db.commit()
                self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to init DB: {e}")

    async def save_reading(self, node_id: int, temperature: float, humidity: float, timestamp: datetime = None):
        """Saves a sensor reading."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Convert to ISO format string to avoid Python 3.12+ DeprecationWarning for default adapter
        ts_str = timestamp.isoformat()
            
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO sensor_readings (timestamp, node_id, temperature, humidity) VALUES (?, ?, ?, ?)",
                    (ts_str, node_id, temperature, humidity)
                )
                await db.commit()
        except Exception as e:
            self.logger.error(f"Failed to save reading: {e}")

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
