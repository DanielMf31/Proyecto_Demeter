# PRD: Python GUI MVP (Control Directo)

## 1. Objetivo
Crear una aplicación de escritorio mínima (Python + Tkinter) que permita controlar los 4 LEDs del ESP32 (Pines 4, 5, 6, 7) enviando tramas binarias directas por UART. Evitando complejidades de gestión de dispositivos.

## 2. Requisitos Técnicos

### 2.1. Comunicación
*   **Puerto:** `/dev/serial0` (Raspberry Pi) o configurable (PC).
*   **Baudrate:** 115200.
*   **Protocolo:** Demeter V2 (Binario).
*   **Transporte:** Debe usar `UartTransport` (modificado para no requerir config) y `DemeterProtocolV2`.

### 2.2. Interfaz Gráfica (Tkinter)
*   **Ventana:** Título "Demeter Control MVP".
*   **Elementos:**
    *   4 Botones grandes: "PIN 4", "PIN 5", "PIN 6", "PIN 7".
    *   Estado visual:
        *   Rojo: Apagado.
        *   Verde: Encendido.
    *   Consola de Texto (Text Area): Para ver los logs de lo que se envía y recibe.

### 2.3. Lógica
*   **Toggle:** Al pulsar un botón, se invierte el estado local y se envía el comando `SET_GPIO`.
*   **Sin Confirmación (MVP):** El botón cambia de color inmediatamente al pulsar (optimista), o imprimimos el ACK si llega.

## 3. Estructura de Archivos
*   `Python/mvp_gui.py`: Archivo único (o principal) que arranca la interfaz.

## 4. Plan de Pruebas
1.  Arrancar `mvp_gui.py`.
2.  Pulsar "PIN 4".
3.  Verificar en consola Python: `TX: FE 03 ...`
4.  (Con Hardware) Verificar que el LED en ESP32 cambia.
