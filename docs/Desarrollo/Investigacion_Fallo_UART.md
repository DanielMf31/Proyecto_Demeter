# Investigación de Fallo en Comunicación UART (Full App)

**Fecha:** 09-02-2026
**Estado:** Hardware Verificado (OK) | Software Fallando (KO)

## 1. Situación Actual
- **Prueba Loopback RPi:** OK (TX se recibe en RX).
- **Prueba `uart_test.cpp` + `monitor_raw.py`:** OK. La RPi recibe perfectamente los paquetes `PING` y `DATA_REPORT` generados por la ESP32.
- **Aplicación Completa (`main_receptor.cpp` + `main.py`):** KO. No se muestra nada en el log de la aplicación Python, o la aplicación parece no recibir datos.

## 2. Hipótesis de Fallo

Dado que el canal físico y la decodificación básica funcionan (probado con `monitor_raw.py`), el problema reside en la **lógica de aplicación**.

### Hipótesis A: Conflicto de Hilos (Threading) en Python (ALTA PROBABILIDAD) 🚨
La librería gráfica **Tkinter NO es segura para hilos (Thread-Safe)**.
1. `UartTransport` ejecuta su bucle `run()` en un hilo secundario (`threading.Thread`).
2. Cuando recibe datos, llama a `self.callback`.
3. El callback en `main.py` invoca directamente métodos de `MainWindow` (`app.log`, `app.handle_data_report`).
4. Estos métodos intentan modificar widgets (como `tk.Text` o `ttk.Treeview`) **desde el hilo de UART**.
5. **Resultado:** En Tkinter, esto suele causar que la actualización se ignore silenciosamente, errores extraños de "Tcl_Async", o que la interfaz se congele. A veces simplemente *no pasa nada*.

**Solución Propuesta:**
Usar `queue.Queue` o el método `root.after_idle` para despachar las actualizaciones a la interfaz gráfica en el hilo principal.

### Hipótesis B: Bloqueo en el Firmware (`main_receptor.cpp`)
Aunque menos probable dado que el `uart_test` funcionó, el firmware completo hace más cosas:
1. **ESP-Now:** Inicializa WiFi. Si hay un conflicto de recursos (ADC2, canales DMA) podría afectar.
2. **Lógica de Ruteo:** `GatewayStrategy` y `ProtocolEngine` tienen lógica para decidir si enviar a UART o ESP-Now.
   - Si el `Engine` cree que el destinatario no es el Host (ID 0) o no está configurado, podría no enviar nada.
   - **Revisión:** Hemos visto que el comando manual 'H' llama a `engine.sendPing(0)`. El ID 0 debería enrutarse a UART por la `GatewayStrategy`.

### Hipótesis C: Buffer Overflow o Race Condition en `UartTransport`
Hemos arreglado el buffer recientemente (`flushInput` y mejor loop), y `monitor_raw.py` demostró que funciona. Sin embargo, si la aplicación completa tarda mucho en procesar el callback (porque intenta pintar en GUI y falla), podría bloquear el hilo de lectura.

## 3. Plan de Acción

### Paso 1: Confirmar Hipótesis A (Python Threading)
Refactorizar `main.py` y `MainWindow` para asegurar que **todas** las interacciones con la GUI ocurran en el hilo principal (`MainThread`).

**Cambios necesarios:**
1. Crear una cola `rx_queue = queue.Queue()` en `MainWindow`.
2. El callback de UART solo pone el comando en la cola: `rx_queue.put(cmd)`.
3. `MainWindow` tiene un método `check_queue()` que se ejecuta periódicamente con `root.after(50, self.check_queue)`, procesa los comandos y actualiza la GUI de forma segura.

### Paso 2: Verificar Firmware
Si tras arreglar lo de Python sigue sin ir, volveremos al Firmware.
- Añadir trazas `Serial.print` en `GatewayStrategy::send` para confirmar que *intenta* escribir en `Serial2`.

## 4. Conclusión Técnica
Es casi seguro un problema de **concurrencia en Python**. Al ejecutar herramientas de CLI (`monitor_raw.py`) no hay GUI ni Tkinter, por eso funcionan. Al usar la App completa, la violación de hilo de Tkinter rompe la comunicación.
