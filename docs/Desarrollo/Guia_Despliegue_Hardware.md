# Guía de Despliegue de Hardware y Firmware - Proyecto Demeter

Esta guía detalla cómo configurar, conectar y programar los dispositivos físicos (ESP32) y la Raspberry Pi para el sistema Demeter V2.

## 1. Inventario de Hardware

| Rol | Hardware | Entorno PlatformIO | Descripción |
| :--- | :--- | :--- | :--- |
| **Gateway** | ESP32-S3 DevKit | `env:gateway` | Puente entre la red de sensores (ESP-NOW) y el servidor (UART). |
| **Nodo Sensor** | ESP32-S3 DevKit | `env:transmisor` | Lee sensores (DHT22, Suelo) y envía reportes. |
| **Nodo Actuador** | ESP32-S3 DevKit | `env:actuador_ventana` | Controla motor/relé y reporta estado/batería. |
| **Servidor** | Raspberry Pi 4/5 | N/A | Ejecuta el servicio Python, Base de Datos y Dashboard. |

---

## 2. Conexiones y Pinout

### A. Gateway (Conectado a Raspberry Pi)
El Gateway se comunica con la Raspberry Pi mediante **UART**.

| Pin ESP32 | Función | Conexión RPi (GPIO Header) | Notas |
| :--- | :--- | :--- | :--- |
| **GPIO 17 (TX)** | UART TX | **GPIO 15 (RXD)** (Pin 10) | Transmite datos A la RPi. |
| **GPIO 16 (RX)** | UART RX | **GPIO 14 (TXD)** (Pin 8) | Recibe comandos DE la RPi. |
| **GND** | Tierra | **GND** (Pin 6/9/Etc) | **¡CRITICO!** Tierras unidas. |
| **GPIO 4** | LED Estado | LED + Resistencia | Parpadea al recibir ACK. |
| **USB** | Alimentación | Puerto USB RPi | Para energía y logs Serial. |

> **Nota:** Asegúrate de que el puerto serial en la RPi esté habilitado (`sudo raspi-config` -> Interface Options -> Serial Port -> Login Shell: NO, Hardware: YES) y sea accesible (usualmente `/dev/serial0` o `/dev/ttyS0`). El código Python usa `/dev/ttyS0` por defecto en modo producción, o `/dev/ttyUSBx` si conectas por USB-Serial.

### B. Nodo Sensor (Entorno `transmisor`)
Este nodo opera de forma inalámbrica (ESP-NOW) y reporta datos.

| Pin ESP32 | Componente | Notas |
| :--- | :--- | :--- |
| **GPIO 4** | Sensor DHT22 (Data) | Temperatura/Humedad Ambiental. |
| **GPIO 5** | Sensor DS18B20 (Data) | Temperatura Suelo (Opcional). |
| **GPIO 34** | Sensor Humedad Suelo (Analog) | Lectura ADC (0-3.3V). |
| **VCC/GND** | Alimentación | Batería o USB. |

> **Nota Código:** Por defecto, el firmware está en modo **MOCK** (`#define USE_MOCK_SENSORS true` en `main_node.cpp`). Si conectas sensores reales, cambia esto a `false` antes de subir.

### C. Nodo Actuador (Entorno `actuador_ventana`)
Controla un motor o relé.

| Pin ESP32 | Componente | Notas |
| :--- | :--- | :--- |
| **GPIO 2** | Relé / LED Motor | Salida Digital (HIGH = ON). |
| **GPIO 35** | Divisor Voltaje (Batería) | Entrada ADC para medir batería. |
| **VCC/GND** | Alimentación | Batería o USB. |

---

## 3. Subida del Firmware

Usa **PlatformIO** para compilar y subir el código a cada ESP32. Asegúrate de seleccionar el entorno correcto.

### Comandos de Terminal (desde carpeta `C++/`)

1. **Subir al Gateway:**
   ```bash
   pio run -e gateway -t upload
   # Opcional: Monitor serie para depurar
   pio device monitor -e gateway
   ```

2. **Subir al Nodo Sensor:**
   ```bash
   pio run -e transmisor -t upload
   ```

3. **Subir al Nodo Actuador:**
   ```bash
   pio run -e actuador_ventana -t upload
   ```

> **Tip:** Si tienes múltiples ESP32 conectados por USB, usa `pio device list` para ver sus puertos (`/dev/ttyACM0`, `/dev/ttyUSB0`) y especifica el puerto de subida en `platformio.ini` o con `--upload-port /dev/ttyX`.

---

## 4. Verificación del Sistema

Una vez todo conectado y encendido:

1. **Inicia el Servicio Python en Raspberry Pi:**
   ```bash
   # En la carpeta Python/
   source .venv/bin/activate
   python main_async.py
   ```
   *Deberías ver logs indicando que el servicio UART ha iniciado.*

2. **Flujo de Datos (Lectura):**
   - El **Nodo Sensor** lee datos (Reales o Mock) cada 5 segundos.
   - Envía vía **ESP-NOW** al Gateway (MAC Address debe estar registrada en el código o emparejada automáticamente).
   - El **Gateway** recibe el paquete ESP-NOW.
   - El Gateway reenvía el paquete vía **UART** a la RPi.
   - **Logs Python**: `[UART] Frame Received: TempHumReport ...`

3. **Flujo de Comandos (Actuación):**
   - En la **GUI** o script de prueba, envía un comando "ABRIR VENTANA" (Target ID 3).
   - **Python** serializa `SET_GPIO(Pin=2, Val=1)` y envía por UART al Gateway.
   - **Gateway** recibe por UART y lo encola/envía por ESP-NOW al Nodo 3.
   - **Nodo Actuador** recibe, activa el Pin 2, y responde con `PIN_REPORT` (nuevo estado) y `ACK`.
   - **Python** recibe el `PIN_REPORT` y actualiza la interfaz (Led "Estado" cambia).

## Solución de Problemas
- **No llegan datos:** Verifica las conexiones TX/RX (deben estar cruzadas: TX->RX, RX->TX).
- **Gateway no recibe de Nodos:** Verifica que las MAC Address en `main_gateway.cpp` (`node2Mac`, etc.) coincidan con las reales de tus ESP32 o implementa el modo de emparejamiento dinámico (comando `ROUTE_ADD`).
- **Permisos Serial:** Si Python falla al abrir el puerto, ejecuta `sudo usermod -a -G dialout $USER` y reinicia.
