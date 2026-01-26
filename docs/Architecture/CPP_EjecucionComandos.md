# Documentación: EjecucionComandos

**Archivo:** `src/Compartidos/EjecucionComandos.cpp` / `include/EjecucionComandos.h`

## Descripción
Clase driver responsable de controlar el hardware físico (actuadores). Gestiona los pines GPIO del ESP32 y controla los tiempos de activación.

## Responsabilidades
*   Mapear IDs de actuadores (1-5) a pines físicos del ESP32.
*   Activar y desactivar pines (Digital Write).
*   Controlar la duración de activación mediante `millis()` (sin `delay` bloqueante).
*   Mantener el estado de qué actuadores están activos.

## Funciones Principales

### `ejecutarComando(int idx)`
Inicia la activación del actuador correspondiente al comando en la posición `idx` del buffer local.
*   Marca el comando como activo.
*   Guarda el tiempo de inicio (`millis()`).

### `verificarCompletados()`
Revisa todos los comandos activos. Si el tiempo transcurrido supera la duración programada, apaga el actuador.
*   **Nota:** Esta función debe usarse con cuidado para no interferir con `MaquinaEstado`.

### `pruebaActuadores()`
Ejecuta una secuencia de test bloqueante, encendiendo cada actuador por 1 segundo secuencialmente. Útil para diagnósticos de hardware.

## Uso en el Sistema
Es controlada principalmente por `MaquinaEstado`. La máquina le dice cuándo encender algo, y `EjecucionComandos` se encarga de apagarlo cuando pasa el tiempo (a menos que la máquina gestione la secuencia).
