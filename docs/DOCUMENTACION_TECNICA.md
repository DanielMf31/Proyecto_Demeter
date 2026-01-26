# Documentación Técnica - Proyecto Demeter

Este documento describe la arquitectura, funcionamiento y mantenimiento del sistema de control automatizado "Proyecto Demeter".

## 1. Visión General del Sistema

El sistema consta de un controlador central (Raspberry Pi 4) que envía secuencias de comandos a un actuador remoto (ESP32-S3) a través de un puerto serial UART. El ESP32 ejecuta estos comandos de forma autónoma y secuencial.

### Arquitectura Física
```mermaid
graph LR
    RPi[Raspberry Pi 4] -- UART (TX/RX) --> ESP32[ESP32-S3]
    ESP32 -- GPIO --> Act1[Actuador 1]
    ESP32 -- GPIO --> Act2[Actuador 2 (etc)]
```

**Conexiones Críticas:**
*   **RPi TX (GPIO 14)** -> **ESP32 RX (GPIO 16)**
*   **RPi RX (GPIO 15)** -> **ESP32 TX (GPIO 17)**
*   **GND (Tierra)** -> **Unida obligatoriamente entre ambos**

---

## 2. Firmware ESP32 (C++)

El código del ESP32 está estructurado bajo **PlatformIO**.

### Estructura de Directorios (`C++`)
*   `platformio.ini`: Configuración de entornos.
    *   `env:receptor`: Código principal de producción (Usa `src/main_receptor.cpp`).
    *   `env:debug`: Código de prueba de hardware (Usa `src/main_debug.cpp`).
*   `src/Compartidos/`:
    *   `ComunicacionUART`: Manejo de bajo nivel del puerto serial (timeout 10ms, buffers).
    *   `ProtocoloComunicacion`: Lógica de paquetes, handshake (101/102) y verificación.
    *   `EjecucionComandos`: Control directo de pines/relés.
    *   `MaquinaEstado`: Orquestador principal. Gestiona los estados (ESPERA, RECIBIENDO, EJECUTANDO).

### Puntos Clave de Mantenimiento
1.  **Race Conditions:** La `MaquinaEstado` y `EjecucionComandos` NO deben intentar detener comandos simultáneamente. La lógica actual prioriza a la máquina si está en estado `EJECUTANDO`.
2.  **Input Serial:** Se usa `Serial.readStringUntil('\n')` con un timeout corto para evitar bloqueos si llegan datos corruptos.

---

## 3. Controlador Raspberry Pi (Python)

El software de control está escrito en Python 3.

### Estructura de Directorios (`Python`)
*   `src/main_poc.py`: Script principal. Inicia el motor de protocolo.
*   `src/uart_service.py`: Wrapper de `pyserial`. Incluye logging de bytes RAW en hexadecimal para depuración de ruido.
*   `src/protocol_engine.py`: Implementación idéntica a la clase C++ del protocolo.

### Uso
```bash
# Ejecutar controlador
python3 Python/src/main_poc.py --port /dev/serial0
```

---

## 4. Protocolo de Comunicación

Protocolo personalizado basado en mensajes ASCII terminados en `\n`.

### Flujo de Conexión
1.  **Handshake:**
    *   RPi envía: `101` (Solicitud)
    *   ESP32 responde: `102` (Confirmación)
2.  **Transmisión de Datos:**
    *   RPi envía 5 paquetes de comandos: `1 1 0 1000 0` (Tipo, Actuador, Param, Duración, Rsv)
    *   RPi espera.
3.  **Verificación (Eco):**
    *   ESP32 envía código `103`.
    *   ESP32 reenvía los 5 comandos recibidos.
    *   RPi compara lo enviado con lo recibido.
4.  **Confirmación Final:**
    *   Si coincide, RPi envía `104` (OK). ESP32 inicia ejecución.
    *   Si falla, RPi envía `105` (Error). ESP32 descarta datos.

---

## 5. Solución de Problemas Comunes

### A. El ESP32 no responde al Handshake (Timeout)
*   **Causa:** Cable GND desconectado o pines RX/TX invertidos.
*   **Solución:** Ejecutar `Python/loopback_test.py` en la RPi con TX unido a RX. Si funciona, revisar cableado al ESP32.

### B. Errores "UnicodeDecodeError" o bytes extraños (0xf8, etc)
*   **Causa:** Ruido eléctrico por falta de referencia de tierra.
*   **Solución:** Conectar cable GND firmemente.

### C. El ESP32 se bloquea y no lee comandos manuales
*   **Causa:** Timeout de `Serial.readStringUntil` demasiado largo.
*   **Solución:** Verificar que `ComunciacionUART.cpp` tiene `serialPort->setTimeout(10)`.

### D. La secuencia se detiene tras el segundo comando
*   **Causa:** Conflicto entre `EjecucionComandos` y `MaquinaEstado`.
*   **Solución:** Asegurar que `verificarCompletados()` solo se llame si la máquina NO está ejecutando (`if (maquina.getEstado() != 3)`).
