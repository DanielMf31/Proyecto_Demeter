# Gateway (Firmware)

El **Gateway** (ID 1) es el puente central entre la red de sensores (ESP-Now) y el Servidor/Host (UART/Serial).

## 1. Descripción General

Actúa como traductor de protocolos y enrutador de mensajes. Utiliza una estrategia de comunicación compuesta (`GatewayStrategy`) para manejar dos interfaces simultáneamente.

*   **Archivo Principal**: `C++/src/main_gateway.cpp`
*   **ID del Nodo**: `1`

## 2. Arquitectura de Comunicación

### Interfaces
1.  **UART (Serial2)**:
    *   Conexión física con Raspberry Pi / PC.
    *   Pines: RX=`16`, TX=`17`.
    *   Baudrate: `115200`.
2.  **ESP-Now**:
    *   Red inalámbrica de sensores.
    *   Canal: 1 (Configurable).

### Estrategia Compuesta (`GatewayStrategy`)
El Gateway inicializa ambas estrategias y permite enrutar mensajes:
*   **Mensajes desde Host (UART)** -> Se envían a Nodos vía ESP-Now.
*   **Mensajes desde Nodos (ESP-Now)** -> Se reenvían al Host vía UART.

## 3. Funcionalidades Clave

### Enrutamiento
*   Mantiene una tabla de rutas (Hardcoded para prototipo):
    *   **Nodo 2**: `9C:13:9E:AC:50:C4`
    *   **Host (ID 0)**: Ruta Serial.

### Procesamiento de Protocolo
Utiliza `ProtocolEngine` y `SystemContext` para una gestión robusta.

*   **Reenvío de Datos (`DataReport`)**:
    *   Al recibir un `TempHumReport` de un nodo, el Gateway lo procesa y lo reenvía al Host (ID 0) para su registro en base de datos.
    *   *Nota*: Actualmente realiza un "proxy", reenviando los datos como si fueran propios o usando mecanismos de reenvío.

*   **Control GPIO Local**:
    *   Responde a comandos destinados a ID 1 (e.g., encender LED de estado).
    *   **Feedback Visual**: GPIO 4 se invierte (toggle) al recibir un ACK, indicando tráfico exitoso.

## 4. Modos de Ejecución (`SystemContext`)
El Gateway implementa modos de ejecución gestionados por `SystemContext`:
1.  **IMMEDIATE**: Procesa comandos UART al instante.
2.  **INTERACTIVE_QUEUE**: Almacena comandos en cola y espera orden de ejecución (útil para depuración o evitar congestión).

## 5. Menú Interactivo (Debug)
A través del puerto Serial USB (no el UART de comunicación), ofrece un menú para pruebas:
*   `H`: Ping al Host.
*   `P`: Ping al Nodo 2.
*   `D`: Enviar reporte de datos simulado al Host.
*   `1-4`: Controlar pines locales manualmente.
