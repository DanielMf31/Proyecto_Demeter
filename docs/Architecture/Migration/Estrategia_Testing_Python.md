# Estrategia de Testing: Backend Python V2

**Estado:** Implementada
**Framework:** `unittest` (Batería estándar de Python)

## 1. Filosofía de Pruebas
Dado que este sistema controla hardware real (bombas, motores), no podemos permitirnos errores en la generación de bytes. Un byte erróneo podría encender una bomba indefinidamente.

Por ello, hemos adoptado una **Pirámide de Testing**:
1.  **Tests Unitarios (Base):** Verifican la lógica matemática (CRC, Structs) aislada.
2.  **Tests de Integración (Mock):** Verifican que los hilos y colas funcionan sin hardware conectado.
3.  **Tests de Sistema (Manual):** Verificación final con hardware real (LEDs).

---

## 2. Suites de Pruebas

### A. `tests/test_protocol_v2.py` (Alta Criticidad)
Verifica que `protocol_v2.py` genera tramas **Bit-Perfect**.
*   **Qué prueba:**
    *   `test_create_set_gpio`: Comprueba que `set_gpio(10, 4, 1)` genera exactamente `FE 03...`.
    *   `test_crc_calculation`: Comprueba que la suma de verificación detecta errores.
    *   `test_create_sequence`: Verifica la compleja trama de secuencias (tiempos y retardos).
*   **Por qué es importante:** Si este test falla, el ESP32 rechazará todos los paquetes por "CRC Error".

### B. `tests/test_device_manager.py` (Configuración)
Verifica que `device_manager.py` es robusto ante errores de usuario.
*   **Qué prueba:**
    *   Carga correcta de `inventory.json`.
    *   **Fallback:** Si borras el JSON, el sistema carga valores por defecto y no crashea.
    *   **Parsing MAC:** Verifica que `AA:BB...` se convierte correctamente a `b'\xaa\xbb...'`.

### C. `tests/test_integration_mock.py` (Arquitectura)
Verifica la comunicación entre hilos (`UI` <-> `Gateway`) simulando el puerto serie.
*   **Qué prueba:**
    *   Que `gateway.send_frame()` mete datos en la cola.
    *   Que el hilo del Gateway saca datos de la cola y llama a `serial.write`.
    *   Que si llegan bytes `FE...` por serial, se dispara el `callback` hacia la UI.
*   **Tecnología:** Usa `unittest.mock.MagicMock` para engañar al programa y hacerle creer que hay un puerto COM conectado.

---

## 3. Cómo Ejecutar los Tests

Desde la carpeta raíz del proyecto (`Proyecto_Demeter/`):

Coamndo para ejecutar **TODOS** los tests:
```bash
python3 -m unittest discover Python/tests
```

Salida Esperada:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.205s

OK
```
