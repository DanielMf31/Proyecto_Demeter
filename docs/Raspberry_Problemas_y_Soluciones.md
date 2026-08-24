# Raspberry Pi Gateway — Problemas que Resuelve y Cómo los Implementa

Este documento cataloga **todos los problemas técnicos** que la capa edge (Raspberry Pi) resuelve, agrupados por categoría. Para cada uno se explica el **concepto teórico** y la **implementación concreta** en el código.

---

## Índice

1. [Puente entre Mundos (UART ↔ WebSocket)](#1-puente-entre-mundos-uart--websocket)
2. [Transporte Serie Asíncrono](#2-transporte-serie-asíncrono)
3. [Codec del Protocolo Binario V2](#3-codec-del-protocolo-binario-v2)
4. [Detección y Ensamblado de Tramas](#4-detección-y-ensamblado-de-tramas)
5. [Traducción Hardware ↔ Software](#5-traducción-hardware--software)
6. [Conexión WebSocket Persistente](#6-conexión-websocket-persistente)
7. [Resiliencia Offline (Store-and-Forward)](#7-resiliencia-offline-store-and-forward)
8. [Persistencia Local (SQLite)](#8-persistencia-local-sqlite)
9. [Auditoría en Disco (CSV)](#9-auditoría-en-disco-csv)
10. [Respuesta Automática al Protocolo](#10-respuesta-automática-al-protocolo)
11. [Configuración Unificada Multi-Capa](#11-configuración-unificada-multi-capa)
12. [Observabilidad y Crash Reports](#12-observabilidad-y-crash-reports)
13. [Testabilidad sin Raspberry Pi](#13-testabilidad-sin-raspberry-pi)
14. [Despliegue Containerizado](#14-despliegue-containerizado)

---

## 1. Puente entre Mundos (UART ↔ WebSocket)

### Problema 1.1: Conectar hardware embebido (binario sobre UART) con cloud (JSON sobre WebSocket)

**Problema:** Los ESP32 hablan protocolo binario a 115200 baud por UART. El backend habla JSON sobre WebSocket/HTTP. Alguien tiene que traducir entre ambos mundos — es el problema central de esta capa.

**Concepto:** Gateway/Mediator Pattern — un orquestador que recibe de un lado, traduce, y envía al otro. Bidireccional.

**Implementación:**
- `command_dispatcher.py` — `GatewayOrchestrator` compone:
  - `UartProcessor` (UART binario ↔ modelos Pydantic)
  - `DemeterWebsocketClient` (JSON ↔ backend cloud)
  - `DeviceManager` (traducción IDs lógicos ↔ físicos)
  - `TelemetryCacheManager` (resiliencia offline)

**Flujo WS → UART (comando del usuario):**
```
Backend WS JSON                    ESP32 UART binary
{"type":"set_gpio",          →     [0xFE][06][00][00][03][10][04][01][00][CRC]
 "pin":1, "value":1}
         │
         ├─ dispatch_ws_to_uart(raw_json)
         ├─ json.loads() → dict
         ├─ device_manager.translate_pin(1) → (node_id=3, pin=4)
         ├─ protocol.validate_json_message(dict) → SetGpio model
         └─ uart.send_command(cmd) → pack_frame() → bytes → UART TX
```

**Flujo UART → WS (telemetría del sensor):**
```
ESP32 UART binary                  Backend WS JSON
[0xFE][04][00][02][00][0B]   →    {"type":"temp_hum_report",
[temp_hi][temp_lo]                  "node_id":2,
[hum_hi][hum_lo][CRC]              "temperature":22.5,
         │                          "humidity":65.3}
         ├─ UartProcessor.process_buffer() → parse_frame()
         ├─ TempHumReport model
         ├─ dispatch_uart_to_ws(cmd)
         ├─ cache.cache_command(cmd) → SQLite + CSV
         └─ ws_client.send_json(cmd.model_dump())
```

### Problema 1.2: Reportar la configuración de hardware al backend automáticamente

**Problema:** El backend necesita saber qué dispositivos hay conectados (bombas, válvulas, IDs) para el frontend de discovery. Sin esto, el frontend no sabe qué botones mostrar.

**Concepto:** Service Discovery — al conectar, el gateway reporta su mapa de hardware.

**Implementación:**
- `command_dispatcher.py` — `report_system_config()`:
  ```python
  async def report_system_config(self):
      config = self.device_manager.mappings  # devices.json content
      await self.ws_client.send_json({
          "type": "system_config",
          "devices": config
      })
  ```
- Se ejecuta en `_on_ws_connect()` — cada vez que el WS reconecta, reporta la config
- El backend almacena en Redis `demeter:discovery:config` → el frontend lo consulta via `GET /api/devices`

---

## 2. Transporte Serie Asíncrono

### Problema 2.1: Leer UART sin bloquear el event loop

**Problema:** La lectura de puerto serie es tradicionalmente bloqueante (`serial.read()` espera hasta que haya datos). En un sistema que también gestiona WebSocket y timers, bloquear en UART congela todo.

**Concepto:** Async Serial I/O — usar `serial_asyncio` para integrar el puerto serie con el event loop de asyncio.

**Implementación:**
- `async_uart.py` — `AsyncUartTransport(TransportStrategy)`:
  ```python
  async def connect(self):
      self.reader, self.writer = await serial_asyncio.open_serial_connection(
          url=self.port, baudrate=self.baud
      )
  ```
- **`_read_loop()`** (asyncio Task):
  - `data = await self.reader.read(1024)` — async, no bloquea
  - Si hay datos → `rx_callback(data)`
  - Si vacío → `await asyncio.sleep(0.1)` (evita busy-wait)
- **`_write_loop()`** (asyncio Task):
  - `data = await self.tx_queue.get()` — espera items sin bloquear
  - `self.writer.write(data)` + `await self.writer.drain()` — backpressure aware

### Problema 2.2: Desacoplar velocidad de recepción de velocidad de procesamiento

**Problema:** Los datos UART llegan a 115200 baud (potencialmente varios frames por ráfaga). El procesamiento (parse + DB + WS) es más lento. Si no hay buffer intermedio, se pierden bytes.

**Concepto:** Producer-Consumer con Queue — el receptor (rápido) encola, el procesador (lento) desencola a su ritmo.

**Implementación:**
- `async_uart.py` — `send()` usa `tx_queue.put_nowait()` (no bloqueante, O(1))
- `uart_processor.py`:
  - RX: `on_uart_data()` acumula en `rx_buffer` (bytearray) — producción inmediata
  - Frame detection: `process_buffer()` extrae frames completos → `rx_queue.put_nowait(cmd)`
  - Consumo: `_dispatch_loop()` await `rx_queue.get()` — procesa cuando hay trabajo

```
UART RX bytes → rx_buffer → process_buffer() → rx_queue → _dispatch_loop()
  (fast)        (bytearray)  (frame assembly)  (Queue)    (slow: DB+WS+callbacks)
```

---

## 3. Codec del Protocolo Binario V2

### Problema 3.1: Serializar modelos Pydantic a bytes binarios para UART

**Problema:** El backend y la Raspberry usan modelos Pydantic (SetGpio, TempHumReport, etc.) para validación y JSON. Pero el ESP32 espera bytes empaquetados. Se necesita un codec bidireccional modelo ↔ bytes.

**Concepto:** Codec con Registry Pattern — un diccionario de funciones de packing/unpacking indexado por tipo de comando.

**Implementación en `demeter_protocol.py` — `DemeterProtocolV2`:**

**Packing (Pydantic → bytes):**
```python
def pack_frame(self, cmd: DemeterCommand) -> bytes:
    if isinstance(cmd, SetGpio):
        payload = struct.pack('<BBB', cmd.pin, cmd.value, cmd.flags)
        cmd_id = CmdId.SET_GPIO
    elif isinstance(cmd, TempHumReport):
        payload = struct.pack('<hh', int(cmd.temperature*100), int(cmd.humidity*100))
        cmd_id = CmdId.TEMP_HUM_REPORT
    # ... 12 tipos más

    header = struct.pack('<BBBBB', len(payload), 0, src, dst, cmd_id)
    crc = sum(header + payload) % 256
    return bytes([0xFE]) + header + payload + bytes([crc])
```

**Unpacking (bytes → Pydantic):**
```python
_registry = {
    CmdId.SET_GPIO: self._parse_set_gpio,
    CmdId.TEMP_HUM_REPORT: self._parse_temp_hum_report,
    CmdId.SENSOR_CLUSTER_REPORT: self._parse_sensor_cluster,
    # ... 12 parsers totales
}

def parse_frame(self, frame: bytes) -> Optional[DemeterCommand]:
    # 1. Validate sync byte, length, CRC
    # 2. Extract cmd_id from header
    parser = self._registry.get(cmd_id)
    return parser(dst, src, payload) if parser else None
```

**Registry Pattern:** extensible sin tocar el core — añadir un nuevo comando solo requiere un parser y una entrada en el dict.

### Problema 3.2: Validar JSON entrante del WebSocket contra los modelos del protocolo

**Problema:** El JSON que llega del backend puede tener campos faltantes, tipos incorrectos, o `type` desconocido. Necesita validación antes de convertir a binario.

**Concepto:** Schema validation con Pydantic TypeAdapter — valida y deserializa en un solo paso.

**Implementación:**
- `demeter_protocol.py` — `validate_json_message(data: dict)`:
  ```python
  def validate_json_message(self, data: dict) -> Optional[DemeterCommand]:
      try:
          return TypeAdapter(AnyDemeterCommand).validate_python(data)
      except ValidationError as e:
          logger.warning(f"Invalid command: {e}")
          return None
  ```
- Usa la misma discriminated union `AnyDemeterCommand` que el backend — **zero schema drift**

---

## 4. Detección y Ensamblado de Tramas

### Problema 4.1: Encontrar tramas válidas en un stream continuo de bytes

**Problema:** UART es un stream — los bytes llegan uno a uno o en ráfagas parciales. Un frame de 12 bytes puede llegar como [8 bytes] + [4 bytes] en dos lecturas separadas. Hay que acumular y detectar tramas completas sin perder datos.

**Concepto:** Frame assembly con buffer circular — acumular bytes, buscar sync byte, verificar longitud declarada, extraer frame completo.

**Implementación en `uart_processor.py` — `process_buffer()`:**
```python
def process_buffer(self):
    while len(self.rx_buffer) >= 7:  # Min frame: header(6) + CRC(1)
        # 1. Buscar SYNC byte
        sync_idx = self.rx_buffer.find(0xFE)
        if sync_idx < 0:
            self.rx_buffer.clear()  # No sync found
            return
        if sync_idx > 0:
            self.rx_buffer = self.rx_buffer[sync_idx:]  # Drop garbage before sync

        # 2. Leer longitud del payload
        if len(self.rx_buffer) < 2: return  # Wait for more data
        payload_len = self.rx_buffer[1]
        total_len = 6 + payload_len + 1  # header + payload + CRC

        # 3. ¿Trama completa?
        if len(self.rx_buffer) < total_len: return  # Wait for more data

        # 4. Extraer y parsear
        frame = bytes(self.rx_buffer[:total_len])
        self.rx_buffer = self.rx_buffer[total_len:]
        cmd = self.protocol.parse_frame(frame)
        if cmd:
            self.rx_queue.put_nowait(cmd)
```

**Recuperación de errores:**
- Si el CRC falla → descarta el byte SYNC y busca el siguiente 0xFE
- Tramas parciales → espera más datos sin perder lo acumulado
- Basura entre tramas → se descarta automáticamente al buscar SYNC

### Problema 4.2: Procesar múltiples tramas en un solo chunk de lectura

**Problema:** A 115200 baud, si el ESP32 envía 3 tramas seguidas, la Raspberry puede recibirlas como un solo bloque de bytes. El parser debe extraer las 3 sin dejar residuo.

**Concepto:** Loop de extracción — mientras haya datos suficientes en el buffer, seguir extrayendo tramas.

**Implementación:**
- `process_buffer()` usa `while len(self.rx_buffer) >= 7:` — sigue extrayendo mientras haya bytes
- Cada trama extraída se elimina del buffer: `self.rx_buffer = self.rx_buffer[total_len:]`
- Si queda un residuo parcial (inicio de la siguiente trama), se mantiene para la próxima lectura

---

## 5. Traducción Hardware ↔ Software

### Problema 5.1: El frontend usa IDs lógicos (pump_1), el hardware usa node_id + pin físico

**Problema:** El usuario pulsa "Bomba 1" en la UI. El frontend envía `{"pin": 1}`. Pero la bomba real está en node_id=3, pin GPIO=4. Esta traducción no debe estar en el frontend (hardcodea hardware) ni en el backend (no conoce el hardware).

**Concepto:** Adapter Pattern — una capa de traducción configurable entre IDs lógicos y físicos, residente en el edge que conoce ambos mundos.

**Implementación:**
- `devices.json` — Mapa declarativo:
  ```json
  {
    "devices": {
      "pump": {
        "1": {"target_id": 3, "physical_pin": 4, "label": "Bomba 1"},
        "2": {"target_id": 3, "physical_pin": 5, "label": "Bomba 2"}
      },
      "valve": {
        "1": {"target_id": 3, "physical_pin": 10, "label": "Válvula 1"}
      }
    }
  }
  ```
- `device_manager.py` — `DeviceManager`:
  - `load_config()` — carga JSON al arrancar
  - `translate_pin(logical_pin)` — heurística: pins 1-4 = pumps, 5-8 = valves → busca en el mapa → retorna `(target_id, physical_pin)`
  - `get_physical_mapping(device_type, logical_id)` — lookup directo

- `command_dispatcher.py` — `_parse_incoming_command()`:
  ```python
  if data.get("type") == "set_gpio":
      target_id, physical_pin = self.device_manager.translate_pin(data["pin"])
      data["target_id"] = target_id
      data["pin"] = physical_pin
  ```
- **Reconfiguración sin recompilar** — cambiar `devices.json` cambia el mapeo sin tocar código

### Problema 5.2: Traducir también los pasos de secuencias

**Problema:** Un `exec_sequence` contiene N pasos, cada uno con un pin lógico. Cada paso necesita traducción individual.

**Implementación:**
- `command_dispatcher.py` — `_parse_incoming_command()`:
  ```python
  if data.get("type") == "exec_sequence":
      for step in data.get("steps", []):
          target_id, physical_pin = self.device_manager.translate_pin(step["pin"])
          step["target_id"] = target_id
          step["pin"] = physical_pin
  ```

---

## 6. Conexión WebSocket Persistente

### Problema 6.1: Mantener conexión permanente con el backend cloud

**Problema:** El backend puede estar en `patata.monters.org` (staging) o en LAN. La conexión WS puede caerse por cortes de internet, reinicios del backend, o timeouts. Necesita reconexión automática infinita.

**Concepto:** Persistent connection loop — bucle infinito que intenta conectar, lee mientras está conectado, y reintenta al desconectar.

**Implementación en `ws_client/client.py` — `DemeterWebsocketClient`:**
```python
async def _connect_loop(self):
    while self.running:
        try:
            uri = f"{self.scheme}://{self.host}:{self.port}/ws/raspberry_gateway"
            async with websockets.connect(uri) as ws:
                self.connection = ws
                if self.on_open_callback:
                    await self.on_open_callback()  # Report config, replay cache
                async for message in ws:
                    await self.on_message_callback(message)
        except websockets.ConnectionClosed:
            logger.warning("WS connection closed. Retrying in 5s...")
        except (ConnectionRefusedError, OSError) as e:
            logger.warning(f"WS connection failed: {e}. Retrying in 5s...")
        except asyncio.CancelledError:
            break  # Clean shutdown
        except Exception as e:
            logger.error(f"WS unexpected error: {e}. Retrying in 5s...")

        self.connection = None
        await asyncio.sleep(5)  # Backoff before retry
```

### Problema 6.2: Detectar esquema WS vs WSS automáticamente

**Problema:** En staging (puerto 443) se usa WSS (TLS). En desarrollo local (puerto 8000) se usa WS plano. No se debe hardcodear.

**Implementación:**
```python
self.scheme = "wss" if settings.BACKEND_PORT == 443 else "ws"
```

### Problema 6.3: Ejecutar acciones al reconectar (replay + discovery)

**Problema:** Cuando el WS reconecta después de una caída, el backend no sabe qué dispositivos hay ni qué telemetría se perdió.

**Concepto:** On-connect hooks — callbacks que se ejecutan al establecer conexión.

**Implementación:**
- `command_dispatcher.py` — `_on_ws_connect()`:
  ```python
  async def _on_ws_connect(self):
      await self.report_system_config()       # Re-report hardware map
      await self.cache.replay_unsynced(self.ws_client)  # Send cached data
  ```
- Se pasa como `on_open_callback` al `DemeterWebsocketClient`

---

## 7. Resiliencia Offline (Store-and-Forward)

### Problema 7.1: No perder telemetría cuando el backend está caído

**Problema:** Si el backend o internet se caen, la Raspberry sigue recibiendo datos del ESP32 por UART. Si solo los envía por WS, se pierden. Esto es inaceptable en un sistema científico.

**Concepto:** Store-and-Forward — almacenar localmente todos los datos con un flag `synced=0`, enviarlos al backend cuando reconecta, marcarlos como `synced=1`.

**Implementación en `telemetry_cache.py` — `TelemetryCacheManager`:**

**Almacenamiento (siempre, con o sin WS):**
```python
async def cache_command(self, cmd: DemeterCommand):
    if isinstance(cmd, TempHumReport):
        await self.db.save_reading(cmd.node_id, cmd.temperature, cmd.humidity)
        self.csv.write_row({...})
    elif isinstance(cmd, SensorClusterReport):
        for entry in cmd.entries:
            await self.db.save_cluster_reading(entry.plant_id, ...)
            self.csv.write_row({...})
```

**Replay al reconectar:**
```python
async def replay_unsynced(self, ws_client):
    # 1. Ambient readings
    rows = await self.db.get_unsynced("sensor_readings", limit=500)
    sent_ids = []
    for row in rows:
        try:
            await ws_client.send_json({
                "type": "temp_hum_report",
                "node_id": row["node_id"],
                "temperature": row["temperature"],
                "humidity": row["humidity"],
                ...
            })
            sent_ids.append(row["id"])
        except:
            break  # Stop on first failure — remaining stay unsynced

    await self.db.mark_synced("sensor_readings", sent_ids)

    # 2. Soil readings (same pattern)
    # ...

    # 3. Cleanup old synced data
    await self.db.cleanup_old(days=30)
    self.csv.cleanup(retention_days=7)
```

**Resiliencia:** Si el envío falla a mitad del replay, los IDs no enviados quedan `synced=0` y se reintentan en el próximo reconect.

---

## 8. Persistencia Local (SQLite)

### Problema 8.1: Almacenar telemetría localmente con mínima infraestructura

**Problema:** La Raspberry necesita almacenar datos offline. PostgreSQL es demasiado pesado. Necesita algo embebido, sin servidor, con soporte async.

**Concepto:** SQLite — base de datos embebida en archivo, cero configuración, con soporte async via `aiosqlite`.

**Implementación en `utils/database.py` — `DatabaseManager`:**

**Dos tablas:**
```sql
-- Telemetría ambiental (por nodo)
CREATE TABLE sensor_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    node_id INTEGER NOT NULL,
    temperature REAL,
    humidity REAL,
    synced INTEGER DEFAULT 0    -- 0=pending, 1=sent to backend
);

-- Telemetría de suelo (por planta)
CREATE TABLE soil_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    plant_id INTEGER NOT NULL,
    soil_temperature REAL,
    soil_moisture REAL,
    synced INTEGER DEFAULT 0
);
```

**Operaciones clave:**
- `save_reading()` / `save_cluster_reading()` — INSERT con `synced=0`
- `get_unsynced(table, limit=500)` — `SELECT WHERE synced=0 ORDER BY timestamp LIMIT 500`
- `mark_synced(table, ids)` — `UPDATE SET synced=1 WHERE id IN (...)`
- `cleanup_old(days=30)` — `DELETE WHERE synced=1 AND timestamp < now-30days`
- `get_stats(node_id, hours=24)` — Agregados AVG/MIN/MAX para dashboards locales

### Problema 8.2: Inicialización idempotente sin migraciones

**Problema:** La Raspberry puede reiniciarse en cualquier momento. La DB debe crearse si no existe y no fallar si ya existe.

**Concepto:** CREATE IF NOT EXISTS — DDL idempotente que es seguro ejecutar N veces.

**Implementación:**
```python
async def init_db(self):
    async with aiosqlite.connect(self.db_path) as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS sensor_readings (...)""")
        await db.execute("""CREATE INDEX IF NOT EXISTS idx_sr_timestamp ...""")
        # Migración inline: añadir columna synced si no existe
        try:
            await db.execute("ALTER TABLE sensor_readings ADD COLUMN synced INTEGER DEFAULT 0")
        except:
            pass  # Column already exists
```

---

## 9. Auditoría en Disco (CSV)

### Problema 9.1: Registro local legible sin software especial

**Problema:** Además de SQLite (para replay programático), se necesita un formato que un investigador pueda abrir en Excel sin herramientas técnicas.

**Concepto:** CSV daily rotation — un archivo CSV por día, auto-rotado, con cleanup automático.

**Implementación en `utils/csv_exporter.py` — `CsvExporter`:**
```python
class CsvExporter:
    HEADERS = ["timestamp", "type", "node_id", "plant_id",
               "temperature", "humidity", "soil_temperature", "soil_moisture"]

    def write_row(self, row: dict):
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = self.csv_dir / f"telemetry_{today}.csv"

        file_exists = filepath.exists()
        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.HEADERS, extrasaction='ignore')
            if not file_exists:
                writer.writeheader()  # Header solo en archivo nuevo
            writer.writerow(row)

    def cleanup(self, retention_days=7):
        # Borra archivos telemetry_YYYY-MM-DD.csv con más de 7 días
```

- Un archivo por día → fácil de encontrar, copiar, enviar por email
- Headers auto-escritos → abre directamente en Excel
- Cleanup cada 7 días → no agota el disco de la SD card

---

## 10. Respuesta Automática al Protocolo

### Problema 10.1: Responder automáticamente a mensajes de control del protocolo

**Problema:** Cuando un ESP32 envía un PING, espera un ACK. Cuando envía un SYN (handshake), espera un SYN_ACK. Si la Raspberry no responde, el nodo entra en estado de error y deja de reportar.

**Concepto:** Protocol-level auto-response — el procesador UART responde automáticamente a mensajes de control antes de pasar los datos a la capa de aplicación.

**Implementación en `uart_processor.py` — `handle_protocol_internal()`:**
```python
async def handle_protocol_internal(self, cmd: DemeterCommand):
    if isinstance(cmd, Ping):
        await self.send_ack(cmd.source_id or cmd.target_id, CmdId.PING)

    elif isinstance(cmd, Syn):
        await self.send_syn_ack(cmd.source_id or cmd.target_id, cmd.context)

    elif isinstance(cmd, SynAck):
        await self.send_ack(cmd.source_id or cmd.target_id, CmdId.SYN_ACK)

    # Ack, Nack, Reports → solo log (no auto-response)
```

- Se ejecuta ANTES de los listeners de aplicación
- Helpers dedicados: `send_ack()`, `send_syn_ack()`, `send_nack()`, `send_ping()`, `send_set_gpio()`
- Cada helper construye el modelo Pydantic → `pack_frame()` → `transport.send()`

---

## 11. Configuración Unificada Multi-Capa

### Problema 11.1: Misma configuración para Backend y Raspberry sin duplicar

**Problema:** Backend y Raspberry necesitan leer variables de entorno como `DEMETER_BACKEND_URL`, `DEMETER_UART_BAUD`, etc. Si cada uno define su propia clase Settings, divergen inevitablemente.

**Concepto:** Shared configuration module — un único `Settings` en `Software/Common/` importado por ambas capas.

**Implementación:**
- `Software/Common/configuration.py` — `Settings(BaseSettings)`:
  - Campos compartidos: `APP_NAME`, `ENV`, `DEBUG`, `BACKEND_URL`, `BACKEND_PORT`
  - Campos solo Backend: `POSTGRES_*`, `REDIS_URL`, `API_PREFIX`
  - Campos solo Raspberry: `PORT` (/dev/serial0), `UART_BAUD` (115200)
  - Campos calculados: `DATA_DIR`, `DB_PATH`, `LOG_FILE_PATH`
- Prefijo `DEMETER_` para todas las env vars
- Lee de `.env` (copiado por Makefile según entorno)

### Problema 11.2: Decidir modo local vs remoto automáticamente

**Problema:** En desarrollo, la Raspberry se conecta a localhost. En staging, a `patata.monters.org:443`. No se debe cambiar código.

**Implementación:**
- `DEMETER_BACKEND_URL` determina el modo:
  - Si definido (staging/prod) → WS a `wss://patata.monters.org:443/ws/raspberry_gateway`
  - Si no definido o `localhost` → WS a `ws://localhost:8000/ws/raspberry_gateway`
- El esquema (ws/wss) se auto-detecta por el puerto (443 = wss)

---

## 12. Observabilidad y Crash Reports

### Problema 12.1: Diagnosticar fallos en un dispositivo remoto sin acceso físico

**Problema:** La Raspberry está en campo, conectada al invernadero. Si algo falla, no hay un desarrollador delante del dispositivo para ver los logs.

**Concepto:** Structured logging + crash reports — logs con nombre de módulo + severidad, y reportes JSON de crash con estado completo.

**Implementación en `utils/logger.py`:**

**Logging:**
```python
def setup_logger(name="demeter"):
    # Handler stdout (console) + handler file (persistent)
    # Format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # Level from settings.log_level
```

**Crash reports:**
```python
def generate_crash_report(state: dict, error: Exception, step_name: str) -> str:
    report = {
        "timestamp": datetime.now().isoformat(),
        "step": step_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc(),
        "state": serialize(state)  # Handles model_dump, __dict__, str fallback
    }
    filepath = f"logs/crashes/crash_{timestamp}_{step_name}.json"
    json.dump(report, open(filepath, 'w'), indent=2)
    return filepath
```

- Los crash reports se guardan en disco para recogida posterior
- Incluyen el estado completo del sistema al momento del fallo

---

## 13. Testabilidad sin Raspberry Pi

### Problema 13.1: Ejecutar tests en CI/CD sin hardware

**Problema:** Los tests necesitan `serial_asyncio`, `RPi.GPIO`, y otros módulos que solo existen en Raspberry Pi OS. En un runner de CI (Ubuntu/Mac), la importación falla.

**Concepto:** Module mocking en conftest — reemplazar módulos de hardware con mocks antes de que se importen.

**Implementación en `tests/conftest.py`:**
```python
import sys
from unittest.mock import MagicMock

# Mock hardware modules before any import
sys.modules['serial_asyncio'] = MagicMock()
sys.modules['serial'] = MagicMock()
sys.modules['RPi'] = MagicMock()
sys.modules['RPi.GPIO'] = MagicMock()

# Add source paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Common"))
```

### Problema 13.2: Tests end-to-end del pipeline UART → Cache → WS

**Problema:** Se necesita verificar que un frame binario que entra por UART termina como JSON en el WebSocket, pasando por SQLite y CSV.

**Concepto:** Integration tests con mocks selectivos — mockear solo el hardware (UART, WS), no la lógica.

**Implementación:**
- `test_telemetry_cache.py` — Tests end-to-end:
  1. Construye frame binario con CRC válido
  2. Alimenta al `UartProcessor` mockeado
  3. Verifica que `cache_command()` inserta en SQLite (`synced=0`)
  4. Verifica que CSV tiene la fila
  5. Simula reconexión WS → `replay_unsynced()` → verifica `send_json()` llamado
  6. Verifica que SQLite marca `synced=1`
  7. Verifica precisión float (round-trip < 0.02°C)

- `test_command_dispatcher.py` — Tests de traducción:
  - WS JSON con pin lógico → verifica que UART recibe pin físico traducido
  - UART TempHumReport → verifica que WS recibe JSON con type correcto

---

## 14. Despliegue Containerizado

### Problema 14.1: Desplegar en Raspberry Pi con dependencias reproducibles

**Problema:** Instalar Python, librerías GPIO, serial_asyncio manualmente en cada RPi es propenso a errores y no reproducible.

**Concepto:** Docker container — imagen con todo incluido, ejecutable en cualquier RPi con Docker.

**Implementación:**
```dockerfile
FROM python:3.11-slim-bookworm
RUN apt-get install -y libgpiod2 gpiod curl
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY Software/Common /app/Software/Common
COPY Software/Raspberry /app/Software/Raspberry
ENV PYTHONPATH="/app/Software/Raspberry/src:/app/Software/Common"
CMD ["python", ".../command_dispatcher.py"]
```

- `make rpi-up` → docker-compose con host networking + device passthrough (`/dev/serial0`)
- Host networking necesario para acceso directo al puerto serie
- `.env.rpi` configura `DEMETER_BACKEND_URL=patata.monters.org` y `DEMETER_BACKEND_PORT=443`

---

## Resumen Visual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                   RASPBERRY PI — PROBLEMAS RESUELTOS                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PUENTE UART↔WS            TRANSPORTE ASYNC       CODEC BINARIO        │
│  ├ GatewayOrchestrator     ├ serial_asyncio        ├ pack_frame()       │
│  ├ Bidireccional           ├ Producer-Consumer     ├ parse_frame()      │
│  └ Service Discovery       └ Backpressure aware    └ Registry Pattern   │
│                                                                         │
│  FRAME ASSEMBLY            TRADUCCIÓN HW↔SW       WS PERSISTENTE       │
│  ├ SYNC byte scanning      ├ devices.json          ├ Reconnect loop     │
│  ├ Partial frame handling  ├ translate_pin()       ├ Auto ws/wss        │
│  └ Multi-frame extraction  └ Sequence translation  └ On-connect hooks   │
│                                                                         │
│  STORE-AND-FORWARD         SQLITE LOCAL            CSV AUDITORÍA        │
│  ├ synced=0/1 flag         ├ 2 tablas (amb+soil)   ├ 1 archivo/día     │
│  ├ Replay on reconnect     ├ Idempotent init       ├ Headers auto       │
│  └ Partial replay safe     └ Async (aiosqlite)     └ Cleanup 7 días    │
│                                                                         │
│  AUTO-RESPONSE             CONFIG COMPARTIDA       OBSERVABILIDAD       │
│  ├ Ping → ACK              ├ Common/Settings       ├ Named loggers      │
│  ├ SYN → SYN_ACK           ├ DEMETER_* envvars     └ JSON crash reports │
│  └ Before app listeners    └ Auto local/remote                          │
│                                                                         │
│  TESTABILIDAD              DESPLIEGUE                                   │
│  ├ Module mocking          ├ Docker slim            │
│  └ E2E pipeline tests      └ Host networking        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
