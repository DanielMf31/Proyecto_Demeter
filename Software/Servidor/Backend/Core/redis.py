import json
import redis.asyncio as redis
from typing import Optional, AsyncGenerator
from .config import get_settings
from .logger import setup_logger

settings = get_settings()
logger = setup_logger("redis_manager")

class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Initializes the Redis connection pool."""
        if not self.redis:
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self.redis.ping()
                logger.info("Connected to Redis.")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}. Running in Standalone Mode (No Pub/Sub).")
                self.redis = None # Ensure it is None so fallback logic works
                # Do NOT raise e

    async def close(self):
        """Closes the Redis connection."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed.")

    async def get_client(self) -> redis.Redis:
        """dependency for FastAPI."""
        if not self.redis:
            await self.connect()
        return self.redis

    # --- A. Device State (Persistent & Cache) ---
    async def set_device_state(self, device_id: int, state: bool):
        """Sets the ON/OFF state of a device (Persistent)."""
        if not self.redis: return
        key = f"device:{device_id}:state"
        value = "ON" if state else "OFF"
        await self.redis.set(key, value)
        # Also publish event
        await self.publish_event("state_change", {"device_id": device_id, "state": value})

    async def cache_device_state(self, device_id: int, state: bool, ttl: int = 60):
        """Caches intended device state for a short period (Default 60s)."""
        if not self.redis: return
        key = f"demeter:cache:device:{device_id}"
        value = "ON" if state else "OFF"
        await self.redis.setex(key, ttl, value)

    async def get_device_state(self, device_id: int) -> bool:
        """Gets the device state, defaults to False (OFF) if not set."""
        if not self.redis: return False
        key = f"device:{device_id}:state"
        value = await self.redis.get(key)
        return value == "ON"

    # --- B. Telemetry (Ephemeral with TTL) ---
    async def save_telemetry(self, sensor_id: int, data: dict, ttl: int = 60):
        """Saves sensor telemetry with a TTL (default 60s)."""
        if not self.redis: return
        key = f"sensor:{sensor_id}:telemetry"
        # Serialize dict to JSON string
        await self.redis.setex(key, ttl, json.dumps(data))

    async def get_telemetry(self, sensor_id: int) -> Optional[dict]:
        """Retrieves active telemetry. Returns None if expired."""
        if not self.redis: return None
        key = f"sensor:{sensor_id}:telemetry"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    # --- C. Event Batching (for ActivityLog) ---
    async def push_activity_event(self, event: dict):
        """Pushes an activity event to a Redis list for batch processing."""
        if not self.redis: return
        await self.redis.lpush("demeter:activity:batch", json.dumps(event))

    async def pop_activity_batch(self, count: int = 100) -> list:
        """Pops a batch of activity events from the Redis list."""
        if not self.redis: return []
        pipe = self.redis.pipeline()
        pipe.lrange("demeter:activity:batch", -count, -1)
        pipe.ltrim("demeter:activity:batch", 0, -(count + 1))
        results = await pipe.execute()
        return [json.loads(e) for e in (results[0] if results else [])]

    # --- D. Pub/Sub System ---
    async def publish_event(self, event_type: str, payload: dict):
        """Publishes an event to the 'iot_events' channel."""
        if not self.redis: return
        message = json.dumps({"type": event_type, "payload": payload})
        await self.redis.publish("iot_events", message)

    async def subscribe_events(self) -> AsyncGenerator[dict, None]:
        """Yields messages from the 'iot_events' channel."""
        if not self.redis: return
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("iot_events")
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield json.loads(message["data"])
        except Exception as e:
            logger.error(f"PubSub error: {e}")
        finally:
            await pubsub.unsubscribe("iot_events")
            logger.info("PubSub unsubscribed.")

# Singleton Instance
redis_manager = RedisManager()

# Dependency for FastAPI
async def get_redis():
    if not redis_manager.redis:
        await redis_manager.connect()
    return redis_manager.redis
