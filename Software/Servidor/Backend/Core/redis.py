import json
import redis.asyncio as redis
from typing import Optional, AsyncGenerator
from .config import get_settings
from .logger import setup_logger

settings = get_settings()
logger = setup_logger("redis_manager")

class RedisManager:
    """
    Gestor centralizado para las conexiones asíncronas con Redis.
    Maneja el pool de conexiones y proporciona métodos auxiliares para 
    cachear telemetría, estados de dispositivos, eventos pub/sub y colas de logs.
    
    Ejemplo de uso general:
        manager = RedisManager()
        await manager.connect()
        await manager.set_device_state(device_id=1, state=True)
    """
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """
        Inicializa el pool de conexiones asíncronas hacia Redis.
        Si la conexión falla, inicializa en modo Standalone (sin Redis).
        """
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
        """
        Establece el estado persistente (ON/OFF) de un dispositivo en Redis y alerta
        por Pub/Sub sobre el cambio.
        
        :param device_id: ID numérico del dispositivo (ej: pin del relé).
        :param state: Booleano indicando el estado deseado (True=ON).
        """
        if not self.redis: return
        key = f"device:{device_id}:state"
        value = "ON" if state else "OFF"
        await self.redis.set(key, value)
        # Also publish event
        await self.publish_event("state_change", {"device_id": device_id, "state": value})

    async def cache_device_state(self, device_id: int, state: bool, ttl: int = 60):
        """
        Guarda temporalmente una orden de cambio de estado enviada a un dispositivo.
        
        :param device_id: ID del dispositivo u actuador.
        :param state: Estado enviado (True=ON).
        :param ttl: Tiempo de vida en segundos antes de expirar.
        """
        if not self.redis: return
        key = f"demeter:cache:device:{device_id}"
        value = "ON" if state else "OFF"
        await self.redis.setex(key, ttl, value)

    async def get_device_state(self, device_id: int) -> bool:
        """
        Recupera el último estado conocido de un actuador.
        
        :param device_id: ID del actuador.
        :return: True si está en ON, False en OFF o si no se encuentra.
        """
        if not self.redis: return False
        key = f"device:{device_id}:state"
        value = await self.redis.get(key)
        return value == "ON"

    # --- B. Telemetry (Ephemeral with TTL) ---
    async def save_telemetry(self, sensor_id: int, data: dict, ttl: int = 60):
        """
        Guarda registros de telemetría de sensores volatilmente para acceso P2P.
        
        :param sensor_id: ID del nodo/sensor emisor.
        :param data: Objeto dict() con las mediciones (ej: TempHumReport).
        :param ttl: Caducidad natural del dato en Redis.
        """
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
        """
        Suma un evento (por ejemplo, encendido de Válvula) a la lista asíncrona,
        permitiendo guardados masivos a la BD (batching) en vez de bloquear el dispatcher.
        
        :param event: Diccionario con la acción, descripcion y device_id.
        """
        if not self.redis: return
        await self.redis.lpush("demeter:activity:batch", json.dumps(event))

    async def pop_activity_batch(self, count: int = 100) -> list:
        """
        Extrae y borra atómicamente un lote de eventos desde la lista asíncrona.
        
        :param count: Máximo número de eventos a extraer en un hit de Pipelining.
        :return: Lista de JSON serializados listos para su Commit a BBDD.
        """
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
