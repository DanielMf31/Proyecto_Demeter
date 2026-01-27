# Documentación Técnica: Backend Python V2 (Migración)

**Fecha:** 27 Enero 2026
**Estado:** Implementado (Fase 1)
**Protocolo:** Demeter V2 (Binario)

## 1. Visión General de la Arquitectura

El nuevo Backend de Python ha sido reescrito desde cero para abandonar el modelo de "scripts sueltos" y adoptar una arquitectura profesional de **Orquestador de Servicios**.

### Principios de Diseño
1.  **Desacoplamiento:** La interfaz gráfica (UI) no sabe nada de bytes. El protocolo no sabe nada de puertos serie.
2.  **No Bloqueante:** La comunicación UART corre en su propio hilo (`Thread`), por lo que la interfaz nunca se congela esperando al hardware.
3.  **Configuración Centralizada:** Todo el sistema se define en un único archivo JSON (`inventory.json`), eliminando el código "hardcoded".

---

## 2. Análisis Detallado de Módulos

### 2.1 Núcleo del Sistema (`src/core/`)

#### A. `protocol_v2.py` (El Cerebro Binario)
Este es el archivo más crítico. Su responsabilidad es **convertir intenciones en bytes**.
*   **Funcionalidad:** Implementa la estructura `struct` definida en el PRD.
*   **Seguridad:** Calcula automáticamente el **CRC** (Checksum) de cada paquete para asegurar que no hay corrupción.
*   **Comandos Clave:**
    *   `create_set_gpio(node, pin, val)`: Genera tramas de actuación instantánea.
    *   `create_sequence(steps)`: Genera la compleja trama de "Lista de Tareas" para el riego secuencial.
*   **Por qué es importante:** Garantiza que Python y C++ hablen exactamente el mismo idioma. Si cambias un byte aquí, debes cambiarlo en el firmware.

#### B. `device_manager.py` (El Mapa del Tesoro)
Es el bibliotecario del sistema.
*   **Carga:** Lee `config/inventory.json` al inicio.
*   **Resolución:** Cuando la UI dice "Activar Riego Norte", este módulo traduce:
    *   "Riego Norte" -> **ID 10**, Pin 4, MAC `24:6F...`.
*   **Sync:** Es capaz de extraer todas las rutas (MACs) para enviárselas al Gateway al inicio.

### 2.2 Capa de Transporte (`src/transport/`)

#### A. `uart_gateway.py` (El Mensajero Incansable)
Maneja la conexión física con el ESP32 Gateway.
*   **Multithreading:** Hereda de `threading.Thread`. Tiene un bucle infinito `while running:` que nunca bloquea al resto del programa.
*   **Cola de Envío:** Usa una `queue.Queue`. Si la GUI manda 50 comandos en 1 segundo, se encolan aquí y se envían ordenadamente uno por uno.
*   **Recepción Activa:** Está siempre escuchando (`serial.read`). Cuando detecta el "Byte Mágico" `0xFE`, captura la trama, la valida y avisa a la aplicación.

### 2.3 Interfaz de Usuario (`src/ui/`)

#### A. `main_window.py` (El Tablero de Control)
Una interfaz Tkinter moderna y dinámica.
*   **Generación Dinámica:** No hemos dibujado botones a mano. El código lee el inventario y **pinta una tarjeta por cada dispositivo** automáticamente. Si añades un sensor al JSON, aparece solo en la pantalla.
*   **Callback:** Se suscribe a los mensajes del Gateway para mostrar respuestas en tiempo real (Logs).

---

## 3. Flujo de Datos: "Vida de un Comando"

Ejemplo: El usuario hace clic en **"Activar Bomba"**.

1.  **GUI (`MainWindow`):** Detecta el clic. Llama a `protocol.create_set_gpio(10, 4, 1)`.
2.  **Core (`ProtocolV2`):**
    *   Empaqueta: `FE 03 01 00 0A 10 ...`
    *   Calcula CRC: `... 45`
    *   Retorna `bytes`.
3.  **Transport (`UartGateway`):**
    *   Recibe los bytes en su `Queue`.
    *   En el siguiente ciclo del `Thread`, los envía por el cable USB (`/dev/ttyACM0`).
4.  **Hardware (Gateway ESP32):** (Futuro) Recibe, procesa y reenvía por ESP-NOW.

---

## 4. Archivos de Configuración

### `config/inventory.json`
Es el corazón de la escalabilidad.
```json
"bomba_norte": {
    "node_id": 10,
    "mac": "AA:BB:CC:DD:EE:FF",  <-- Vital para el enrutamiento V2
    "pin": 4,
    "type": "RELAY"
}
```
Para añadir un nuevo dispositivo, **solo editas este archivo**. No tocas código Python.

---

## 5. Próximos Pasos (Migración C++)

Ahora que Python es capaz de generar estas tramas perfectas, el ESP32 actual (V1) no entenderá nada.
El siguiente paso es borrar el código del ESP32 y escribir el **Firmware V2** que tenga:
1.  **Parser Binario:** Para entender el `0xFE`.
2.  **Tabla de Rutas:** Para guardar las MACs que Python le envíe.
3.  **Motor de Secuencias:** Para ejecutar las listas de tareas.
