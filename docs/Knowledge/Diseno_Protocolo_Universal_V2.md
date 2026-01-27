# Teoría y Diseño de Protocolos de Comunicación (Demeter V2)

Este documento recoge la teoría fundamental sobre protocolos de comunicación embebidos y establece los requisitos y la propuesta de diseño para la versión 2.0 del protocolo Demeter, orientada a ser **Universal** (UART, LoRa, ESP-NOW, WiFi).

## 1. Teoría Fundamental: Anatomía de un Paquete (Frame)
A diferencia de enviar texto plano (que es frágil), los protocolos profesionales encapsulan la información en **Tramas** o **Paquetes** binarios.

Una trama estándar "tipo industrial" suele tener esta estructura:

| Campo | Tamaño (Bytes) | Descripción | Analogía Postal |
| :--- | :--- | :--- | :--- |
| **SYNC** | 1 | "Número Mágico" que indica donde empieza un mensaje. Ej: `0xFE`. | El Sobre |
| **LEN** | 1 | Cuántos bytes vienen a continuación. Vital para lectura dinámica. | El peso del paquete |
| **SEQ** | 1 | Contador (0-255) para detectar paquetes perdidos o duplicados. | Sello fechador |
| **SYS_ID** | 1 | ID del sistema que envía (Quién soy). | Remitente |
| **COMP_ID** | 1 | ID del componente específico (Ej. Brazo 1, Sensor 2). | Departamento |
| **MSG_ID** | 1 | Qué operación se solicita (SET, GET, ERROR). | Asunto |
| **PAYLOAD** | 0-N | Los datos útiles (Variables, Texto, Estructuras). | La carta en sí |
| **CRC** | 1-2 | Matemáticas para asegurar que no hubo corrupción de bits. | Sello de lacre |

---

## 2. Análisis de Estándares Existentes

Antes de diseñar, miremos qué usan los pros:

### A. MavLink (El Estándar de Drones)
*   **Filosofía:** "Dispara y olvida" (stream de datos) + Comandos críticos garantizados.
*   **Pros:** Súper robusto, librerías en todos los idiomas (C, Python, Java). Estructura muy probada.
*   **Contras:** Header grande (min 8 bytes). Excesivo para encender una bombilla.

### B. Modbus RTU (El Abuelo Industrial)
*   **Filosofía:** Maestro-Esclavo estricto. El Maestro pregunta, Esclavo responde.
*   **Pros:** Estándar mundial en PLCs. Simple.
*   **Contras:** Muy rígido. No permite que un sensor "avise" de algo voluntariamente (solo si le preguntan). No apto para Mesh.

### C. MQTT-SN (Sensor Networks)
*   **Filosofía:** Pub/Sub para redes no-TCP (UDP, Zigbee, LoRa).
*   **Pros:** Muy flexible (Topics).
*   **Contras:** Requiere un "Broker" o Gateway central. Aumenta la complejidad de infraestructura.

---

## 3. Propuesta de Diseño: Protocolo Demeter V2 (DDP)

Para Demeter, buscamos un híbrido: la ligereza de un protocolo custom con la estructura de MavLink.

### Estructura de Trama (Header: 6 Bytes) - Ideal para LoRa
```text
[SYNC] [LEN] [FLAGS] [SRC] [DST] [CMD]  [...PAYLOAD...]  [CRC]
  0      1      2      3     4     5         6...N        N+1
```

*   **SYNC (0xFE):** Inicio.
*   **FLAGS:**
    *   `Bit 0`: ACK Request (¿Contéstame?).
    *   `Bit 1-2`: Prioridad.
*   **SRC/DST:** IDs de 1 Byte (255 disp). `0` = Master, `255` = Broadcast.
*   **CMD:** ID de instrucción (Ej: `CMD_SET_ACTUATOR = 0x10`).

---

## 4. Migración: De V1 (Texto) a V2 (Binario)

Aquí tienes la comparativa real de byte a byte.

### Caso 1: Handshake (Ping)
*   **V1 (Actual):** Envía string `"101\n"`. (4 bytes ASCII).
*   **V2 (Propuesta):**
    *   Header: `FE 00 01 01 02 PING` (6 bytes).
    *   Payload: Vacío.
    *   CRC: 1 byte.
    *   **Total: 7 Bytes.**
    *   *Veredicto:* V2 es más grande pero **seguro**. Sabes quién lo pide y si se corrompió.

### Caso 2: Activar Actuador (Comando Complejo)
*   **V1 (Actual):** `"1 1 0 1000 0\n"` (Cadena de ~12-14 bytes).
    *   Parser: Lento (split string, atoi...). Miedo a espacios extra.
*   **V2 (Propuesta):**
    *   Header: `FE 05 00 01 02 CMD_ACT` (6 bytes).
    *   Payload: `[TIPO][ID][VAL][DUR_L][DUR_H]` (5 bytes binarios).
    *   CRC: 1 byte.
    *   **Total: 12 Bytes.**
    *   *Veredicto:* Mismo tamaño, pero parseo instantáneo (memcpy) y a prueba de balas.

---

## 5. Implementación con LoRa: Lo que debes saber

LoRa no es WiFi. Es un walkie-talkie lento de muy largo alcance.

### A. Airtime (Tiempo en Aire)
*   Tardar 0.5 segundos en enviar un mensaje es "normal" en LoRa.
*   **Consecuencia:** Si envías mensajes ASCII largos, colapsas la red. El binario es obligatorio.

### B. Duty Cycle (Normativa Legal)
*   En Europa (868MHz), por ley solo puedes transmitir el **1% del tiempo**.
*   Si tu mensaje tarda 1 segundo en enviarse, tienes que callarte 99 segundos.
*   **Estrategia:** Protocolo V2 minimiza bytes = minimiza silencio obligado.

### C. Direccionamiento
*   En LoRa, todos escuchan todo (es radio abierta).
*   Tu protocolo V2 **DEBE** filtrar por `DST`.
    *   Si `DST` no es mi ID, descarto el paquete inmediatamente y me duermo para ahorrar batería.

### D. ACK Aleatorio
*   Si haces un Broadcast (`DST=255`) "Apagar Todo", y pides ACK... 50 dispositivos responderán a la vez y chocarán.
*   **Solución:** Los dispositivos esperan un tiempo aleatorio (Jitter) antes de responder a un Broadcast.

## 6. Siguientes Pasos Técnicos (Roadmap)

1.  **Endianness:**
    *   Definir si enviamos `int16` como `[High, Low]` (Big Endian) o `[Low, High]` (Little Endian). Sugerencia: Little Endian (estándar en ARM/ESP32).
2.  **Librería Compartida (`DemeterLink`):**
    *   Crear una carpeta `common/` con un `struct` en C++ que sea idéntico a una clase `Struct` en Python.
    *   Esto asegura que ambos hablen el mismo idioma binario sin errores.

---

## 7. Ejemplos Prácticos de Implementación

Para que entiendas cómo se traduce esto de "Idea" a "Bytes reales" en el código.

### A. Estructura de Datos (El Molde)

Definimos una plantilla (Struct) que sea idéntica en C++ y Python.

**En C++ (ESP32):**
```cpp
// Usamos #pragma pack(1) para que no haya espacios vacíos entre bytes
#pragma pack(push, 1)
struct DemeterFrame {
    uint8_t sync;       // 1 byte (0xFE)
    uint8_t length;     // 1 byte
    uint8_t flags;      // 1 byte
    uint8_t source_id;  // 1 byte
    uint8_t dest_id;    // 1 byte
    uint8_t command_id; // 1 byte
    uint8_t payload[5]; // 5 bytes (Ejemplo para actuadores)
    uint8_t crc;        // 1 byte
};
#pragma pack(pop)
```

**En Python (Raspberry Pi):**
Usamos la librería `struct` que ya viene instalada.
```python
import struct

# Formato: '<BBBBBB5sB'
# < : Little Endian
# B : Unsigned Char (1 byte)
# 5s: 5 bytes de char/string
fmt = '<BBBBBB5sB'
```

### B. Ejemplo: Comando "Encender Luz" (ID 1, Valor 100)

Imagina que queremos enviar: "Actuador 1, Tipo 1, Valor 100, Duración 0".

**1. Lo que pensamos (Humano):**
*   Origen: Master (0)
*   Destino: Nodo Cocina (10)
*   Comando: SET_ACTUATOR (0x10)
*   Payload: `01 01 64 00 00` (Tipo 1, ID 1, Val 100, Dur 0)

**2. Lo que viaja por el cable (Binario):**
Hexadecimal: `FE 05 00 00 0A 10 01 01 64 00 00 CS`

---

## 8. Arquitectura de Red: Gateway y Registro de Dispositivos (Device Registry)

Esta sección define cómo organizaremos la red para hacerla mantenible a gran escala (256+ nodos).

### A. Filosofía: "Cerebro Central, Músculo Distribuido"
En lugar de que cada ESP32 sepa "quién es quién", **centralizamos toda la inteligencia en la Raspberry Pi**.
*   **Raspberry Pi:** Conoce la lista completa de dispositivos (Registro). Sabe que "Bomba 3" está en el Nodo 15, Pin 4.
*   **Gateway (ESP32 #1):** Solo recibe bytes por USB y los repite por radio (LoRa/ESP-NOW). Es "transparente".
*   **Nodos (ESP32 #N):** Son "tontos". Solo obedecen: "Pon mi Pin 4 en ALTO". No saben si mueven una bomba o un ventilador.

### B. El Registro Maestro (`inventory.json`)
La Raspberry Pi mantiene un archivo de configuración que mapea nombres humanos a direcciones físicas.

```json
{
  "devices": {
    "bomba_riego_norte": {
      "node_id": 15,
      "hw_pin": 4,
      "type": "RELAY_NO",
      "description": "Bomba principal zona norte"
    },
    "sensor_humedad_tomates": {
      "node_id": 12,
      "hw_pin": 34,
      "type": "ANALOG_INPUT",
      "calibrate_offset": 0.5
    }
  }
}
```

### C. Flujo de Ejecución (Paso a Paso)

Si un usuario pulsa "ACTIVAR RIEGO NORTE" en la GUI:

1.  **GUI (Python):** Llama a `DeviceManager.activate("bomba_riego_norte")`.
2.  **Device Manager:**
    *   Consulta el JSON.
    *   Traduce: "Ah, eso es **Nodo 15**, **Pin 4**".
    *   Genera comando binario: `DST=15, CMD=SET_GPIO, PIN=4, VAL=1`.
3.  **UART Service:** Envía la trama binaria (`FE ...`) por USB al Gateway.
4.  **Gateway (ESP32):**
    *   Recibe la trama.
    *   Ve que `DST != 0` (no es para mí).
    *   Retransmite la trama intacta por LoRa/ESP-NOW.
5.  **Nodo Destino (ID 15):**
    *   Recibe la trama por radio.
    *   Ve que `DST == 15` (es para mí).
    *   Ejecuta: `digitalWrite(4, HIGH)`.

### D. Ventajas de esta Arquitectura
1.  **Flexibilidad Total:** Si se quema el ESP32 de la bomba y pones uno nuevo (con ID diferente), solo editas el JSON en la RPi. No tienes que recompilar código C++.
2.  **Gateway Intercambiable:** El Gateway no tiene configuración. Si se rompe, pones cualquier ESP32 virgen con el código de "Repetidor" y funciona.
3.  **Escalabilidad:** Añadir un nuevo sensor es tan fácil como pegarle una etiqueta y añadir una línea al JSON.

---

## 9. Catálogo de Comandos y Estrategia de Alta Densidad (Batching)

A continuación, la lista completa (Diccionario Hexadecimal) y cómo resolver el problema de enviar datos de 12 plantas a la vez de forma eficiente.

### A. Catálogo Maestro de Comandos

Estos son los valores que pondremos en el byte `CMD` (Índice 5 del Header).

| Hex | Nombre | Payload Esperado | Descripción |
| :--- | :--- | :--- | :--- |
| **0x01** | `CMD_PING` | 0 Bytes | "¿Estás vivo?" |
| **0x02** | `CMD_ACK` | 0 Bytes | "Mensaje recibido correctamente" |
| **0x03** | `CMD_NACK` | 1 Byte (Error Code) | "Error en mensaje anterior" |
| **0x10** | `CMD_SET_GPIO` | 3 Bytes: `[PIN][VAL][FLAGS]` | Control digital simple (Relés, LEDs) |
| **0x11** | `CMD_SET_PWM` | 3 Bytes: `[PIN][VAL_L][VAL_H]` | Control analógico (Motores, Luces) |
| **0x20** | `CMD_GET_SENSORS` | 0 Bytes | "Dame tus lecturas ahora" |
| **0x21** | `CMD_REPORT_SINGLE` | 4 Bytes: `[ID][TYPE][VAL_L][VAL_H]` | Reporte de un solo sensor |
| **0x22** | `CMD_REPORT_BATCH` | **Variable (Ver abajo)** | Reporte masivo comprimido |

---

### B. Estrategia "High Density" (12 Plantas x 2 Sensores = 24 Sensores)

El problema: Si enviamos 24 mensajes separados (uno por sensor), saturamos la red LoRa (Airtime excesivo).
La solución: **Agregación de Datos (Batching)** en un solo paquete.

#### Cálculo de Tamaño
Si tenemos 12 plantas, y cada planta tiene Humedad (2 bytes) y Temperatura (2 bytes):
*   Total datos puros: 12 * (2+2) = **48 Bytes**.
*   Header Protocolo: **6 Bytes**.
*   **Total Paquete: 54 Bytes.**

¡Excelente noticia! El límite de LoRa (incluso en configuraciones lentas) suele rondar los 200 bytes. **Podemos enviar TODO el estado del invernadero en UN SOLO mensaje.**

#### Estructura del Payload `CMD_REPORT_BATCH (0x22)`

No enviamos "Sensor 1: Valor X", "Sensor 2: Valor Y". Eso gasta espacio.
Como la Raspberry Pi ya sabe el orden (gracias al `inventory.json`), enviamos solo los valores crudos en orden fijo.

**Estructura del Payload (Binario):**
```text
[TIMESTAMP (4B)] [COUNT (1B)] [VAL_0 (2B)] [VAL_1 (2B)] ... [VAL_23 (2B)]
```
*   `TIMESTAMP`: Tiempo del ESP32 (millis) para sincronizar.
*   `COUNT`: Número de sensores incluidos (24).
*   `VAL_X`: Valor `int16` (entero 16 bits).

**Comparativa de Eficiencia:**
*   **Método Ingenuo (JSON Texto):** `{"p1_hum": 50, "p1_temp": 25...}` -> ~400-500 bytes. (¡Demasiado para LoRa!)
*   **Método Demeter V2 Batch:** 54 bytes. (**10 veces más rápido**).

### C. Buffering y Fragmentación (Store & Forward)

¿Qué pasa si el ESP32 pierde conexión con la Raspberry Pi o el Gateway?

1.  **Buffer Circular:** El ESP32 guarda las lecturas en un Array en RAM cada X minutos.
    *   ESP32 tiene ~300KB RAM. Guardar 100 lecturas de 48 bytes ocupa apenas 5KB. Podríamos guardar datos de **días** si fuera necesario.
2.  **Ráfaga (Burst Mode):** Cuando el Gateway pregunta (`CMD_GET_BATCH_HISTORY`), el ESP32 envía todos los paquetes guardados uno tras otro.

#### ¿Fragmentación?
Si alguna vez superamos los 200 bytes (ej. 50 plantas en un solo micro), usamos paquetes secuenciales:
*   Paquete 1/3: Sendas 0-20.
*   Paquete 2/3: Plantas 21-40.
*   Paquete 3/3: Plantas 41-50.
*   En el Header usamos el bit de flag `MORE_DATA` para indicar que "viene otro paquete detrás".

Esto permite escalar a sistemas masivos sin cambiar el hardware.

---

## 10. Ejemplo Real de Flujo de Datos (Trace)

A continuación, la secuencia hexadecimal **EXACTA** que viajaría por el cable para los casos de uso que pediste.
*Nota: `XX` representa el CRC calculado.*

### Escenario A: Encender Actuadores Secuencialmente (5 Segundos c/u)
**Objetivo:** Verificar conexión, encender Bomba 1 (Pin 4) por 5 segundos, luego Bomba 2 (Pin 5) por 5 segundos.
**Nodos:** Master (0x00), Nodo Actuador (0x0A).

#### 1. Handshake (Verificar Vida)
*   **Master -> Nodo (Ping):** `FE 00 01 00 0A 01 XX`
    *   `FE`: Sync
    *   `00`: Len 0
    *   `01`: Flag ACK REQUEST
    *   `00`: Src (Master)
    *   `0A`: Dst (Nodo 10)
    *   `01`: Cmd (PING)
*   **Nodo -> Master (Ack):** `FE 00 00 0A 00 02 XX` (ACK)

#### 2. Encender Bomba 1 (Pin 4, 5 Segundos)
*   **Master -> Nodo:** `CMD_SET_GPIO_TIMED` (Inspirado en 0x1x)
    *   Comando definido para ejemplo: `0x15` (Timed Actuator)
    *   Payload necesario: `[PIN] [VAL] [TIME_L] [TIME_H]` (4 bytes)
    *   5000ms = `0x1388` -> Little Endian: `88 13`
    *   **Trama:** `FE 04 01 00 0A 15 04 01 88 13 XX`
        *   `04`: Len Payload
        *   `15`: Cmd Timed
        *   `04`: Payload Pin
        *   `01`: Payload Val (HIGH)
        *   `88 13`: Payload Dura (5000ms)
*   **Nodo -> Master:** `FE 00 00 0A 00 02 XX` (ACK, recibido ok)

*(Pasan 5 segundos... el nodo apaga el pin automáticamente)*

#### 3. Encender Bomba 2 (Pin 5, 5 Segundos)
*   **Master -> Nodo:** `FE 04 01 00 0A 15 05 01 88 13 XX`
*   **Nodo -> Master:** `FE 00 00 0A 00 02 XX`

---

### Escenario B: Obtener Datos de 12 Plantas (Full Snapshot)
**Objetivo:** Leer 24 sensores (12 Humedad, 12 Temp) de un solo golpe.
**Nodos:** Master (0x00), Nodo Sensor (0x14 - ID 20).

#### 1. Solicitud (Master Pide)
*   **Master -> Nodo:** `FE 00 00 00 14 20 XX`
    *   `14`: Dst (20)
    *   `20`: Cmd GET_SENSORS

#### 2. Respuesta (Nodo Escupe Todo)
*   El nodo responde con `CMD_REPORT_BATCH (0x22)`.
*   Payload: `[Time 4B][Count 1B][Data...]`
*   Supongamos Timestamp 1000ms (`e8 03 00 00`) y 4 sensores de ejemplo (para no escribir los 24 aquí):
    *   S1 (Hum): 60% (`3c 00`)
    *   S2 (Temp): 25C (`19 00`)
*   **Trama Respuesta:**
    `FE 09 00 14 00 22 E8 03 00 00 02 3C 00 19 00 XX`
    *   `09`: Len (4 Time + 1 Count + 4 Data) = 9 Bytes.
    *   `14`: Src (Nodo 20)
    *   `00`: Dst (Master)
    *   `E8 03 00 00`: Timestamp
    *   `02`: Count (2 sensores en este ejemplo recortado)
    *   `3C 00`: Valor 1 (60)
    *   `19 00`: Valor 2 (25)

Esta trama compacta es lo que permite tener cientos de plantas sin saturar la red.

---

## 11. Estrategia de Implementación Unificada (Polimorfismo)

¿Cómo hacemos que esto funcione igual por UART, LoRa o ESP-NOW sin volvernos locos reescribiendo código? Utilizando el patrón de diseño **Transport Interface**.

### A. Concepto de "Transporte Agnóstico"
El `ProtocolEngine` (el cerebro) **NO DEBE SABER** si está usando un cable o una antena. Solo sabe que quiere enviar `bytes` a `ID 3`.

### B. Implementación en C++ (Clases Abstractas)

Creamos una clase base llamada `DemeterTransport`.

```cpp
class DemeterTransport {
    public:
        virtual void init() = 0;
        virtual bool send(uint8_t targetID, uint8_t* data, size_t len) = 0;
        virtual int receive(uint8_t* buffer, size_t maxLen) = 0;
};
```

Luego, creamos las "Hijas" específicas:

1.  **`UARTTransport`**:
    *   `send(...)`: Hace `Serial.write(data, len)`. Ignora el `targetID` si es punto a punto, o lo usa si es RS485.
2.  **`LoRaTransport`**:
    *   `send(...)`: Hace `LoRa.beginPacket()`, escribe los `bytes`, `LoRa.endPacket()`.
3.  **`EspNowTransport`**:
    *   `send(...)`: Busca la MAC Address asociada al `targetID` y hace `esp_now_send(mac, data...)`.

### C. Ventaja Brutal
*   En tu `main.cpp`, puedes tener:
    ```cpp
    #ifdef USAR_LORA
        LoRaTransport transport;
    #else
        UARTTransport transport;
    #endif
    
    ProtocolEngine engine(&transport); // ¡El motor es el mismo!
    ```
*   Esto significa que si mañana inventan una nueva radio super potente, solo escribes una clase `NewRadioTransport` y **el 99% de tu código (la lógica de bombas, sensores, protocolo) sigue siendo idéntico**.

---

## 12. Implementación Completa de Referencia (Python POC)

A continuación, una clase en Python (lista para copiar y pegar) que implementa todo el flujo: Carga el JSON, busca el ID del dispositivo y genera la trama binaria exacta lista para enviar por USB.

### Código `poc_protocol_v2.py`

```python
import struct
import json

# ==========================================
# 1. Simulación del Archivo inventory.json
# ==========================================
INVENTORY_MOCK = """
{
    "devices": {
        "bomba_riego_norte": { 
            "node_id": 15, 
            "pin": 4, 
            "type": "RELAY", 
            "description": "Bomba principal" 
        },
        "luces_crecimiento": { 
            "node_id": 6, 
            "pin": 12, 
            "type": "PWM", 
            "description": "Luces LED PWM" 
        }
    }
}
"""

# ==========================================
# 2. Clases del Sistema
# ==========================================

class DeviceManager:
    """Encargado de traducir nombres humanos a NodeID + Pin"""
    def __init__(self, json_content):
        self.data = json.loads(json_content)
        self.devices = self.data["devices"]

    def get_target(self, device_name):
        dev = self.devices.get(device_name)
        if not dev:
            return None
        return (dev["node_id"], dev["pin"])

class DemeterProtocolV2:
    """Motor que convierte intenciones en bytes"""
    CMD_SET_GPIO = 0x10
    
    def __init__(self):
        self.seq = 0
        
    def pack_command(self, target_node_id, cmd_id, payload_bytes):
        # Header Structure: 
        # [SYNC(1)] [LEN(1)] [FLAGS(1)] [SRC(1)] [DST(1)] [CMD(1)]
        
        sync = 0xFE
        length = len(payload_bytes)
        flags = 0x01 # Request ACK
        src_id = 0x00 # Master (Raspberry)
        
        # Empaquetamos el Header (6 bytes)
        # B = unsigned char (1 byte)
        header = struct.pack('<BBBBBB', sync, length, flags, src_id, target_node_id, cmd_id)
        
        # Incrementamos secuencia (simulado)
        self.seq = (self.seq + 1) % 255
        
        return header + payload_bytes + b'\x00' # Dummy CRC

    def create_actuator_frame(self, target_node, pin, value):
        # Payload para CMD_SET_GPIO (0x10):
        # [PIN] [VAL] [FLAGS_EXTRA]
        payload = struct.pack('<BBB', pin, value, 0)
        return self.pack_command(target_node, self.CMD_SET_GPIO, payload)

# ==========================================
# 3. Demostración de Flujo (Main)
# ==========================================

def demo_activar_bomba():
    print("--- INICIANDO DEMO V2 ---")
    
    # 1. Inicializar Sistemas
    manager = DeviceManager(INVENTORY_MOCK)
    protocol = DemeterProtocolV2()
    
    # 2. Solicitud de Usuario (Viene de la GUI)
    target_name = "bomba_riego_norte"
    print(f"Usuario solicita activar: '{target_name}'")
    
    # 3. Resolución de Dirección (Device Registry)
    target_info = manager.get_target(target_name)
    if not target_info:
        print("ERROR: Dispositivo no encontrado")
        return
        
    node_id, pin = target_info
    print(f"  -> Mapeado a: Nodo {node_id}, Pin {pin}")
    
    # 4. Generación de Paquete Binario
    packet = protocol.create_actuator_frame(node_id, pin, 1) # 1 = ON
    
    # 5. Visualización Hexadecimal (Simulando envío UART)
    hex_dump = ' '.join(f'{b:02X}' for b in packet)
    print(f"  -> Trama Generada (Bytes): {len(packet)} bytes")
    print(f"  -> [ {hex_dump} ]")
    print("Enviando por UART... (Simulado)")

if __name__ == "__main__":
    demo_activar_bomba()
```

### Resultado Esperado al Ejecutar
```markdown
Usuario solicita activar: 'bomba_riego_norte'
  -> Mapeado a: Nodo 15, Pin 4
  -> Trama Generada (Bytes): 10 bytes
  -> [ FE 03 01 00 0F 10 04 01 00 00 ]
```
*Observa cómo `0F` es el Nodo 15 y `10` es el comando SET_GPIO.*

---

## 13. Experiencia de Usuario: Auto-Descubrimiento y "Zero-Config"

Para que el sistema sea comercial (instalable por cualquiera), añadiremos una capa de **Auto-Provisión** inspirada en el emparejamiento Bluetooth.

### A. El Problema
Si vendes un "Kit de Expansión (Bomba)", el usuario NO sabe de IDs ni de JSONs. Solo quiere enchufarlo.

### B. El Flujo "Plug & Play" (Propuesta)

1.  **Estado de Fábrica:**
    *   Todos los ESP32 nuevos vienen con `NODE_ID = 254` (Unprovisioned).
    *   Al encenderse, parpadean en rojo y emiten `CMD_HELLO (0x04)` cada 10 segundos.

2.  **Detección en Raspberry Pi:**
    *   El Gateway recibe el `CMD_HELLO` de un nodo desconocido.
    *   La GUI muestra un popup: *"¡Nuevo Dispositivo Detectado! ¿Desea configurarlo?"*

3.  **Configuración Visual (Wizard):**
    *   El usuario hace clic en "Sí".
    *   Selecciona tipo: "Es una Válvula de Riego".
    *   Le pone nombre: "Riego Jardín".

4.  **Provisión Automática:**
    *   La Raspberry Pi busca el primer ID libre (ej. 16).
    *   Envía comando especial `CMD_CONFIG (0x05)`:
        *   Payload: `[NEW_ID=16] [SAVE_TO_EEPROM=1]`
    *   El ESP32 guarda el ID 16 en su memoria permanente, se reinicia y parpadea en verde.
    *   La Raspberry Pi añade la entrada a `inventory.json` automáticamente.

### C. Resultado
El usuario **NUNCA toca código**. Solo conecta cables y hace clic en "Aceptar" en la pantalla táctil.

### D. Interfaz de Usuario Sugerida (Mockup Lógico)

| Panel de Control | Panel de Configuración |
| :--- | :--- |
| [ Btn: Riego Norte ] | **Dispositivos Nuevos:** |
| [ Btn: Luces LED ] | [ ! ] Nodo #254 (Señal: -40dBm) |
| [ Btn: Ventilador ] | [ Botón: ASIGNAR ] |

Al pulsar "ASIGNAR", se abre un formulario simple:
*   Nombre: `___________`
*   Tipo: `[ Bomba / Luz / Sensor ]`
*   Pin Físico: `[ 4 ]` (Predefinido por el hardware del kit)

Esto transforma el proyecto de un "experimento maker" a un **producto profesional**.