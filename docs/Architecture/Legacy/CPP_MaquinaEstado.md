# Documentación: MaquinaEstado

**Archivo:** `src/Compartidos/MaquinaEstado.cpp` / `include/MaquinaEstado.h`

## Descripción
El cerebro del sistema de recepción. Orquesta el flujo global de la aplicación, decidiendo cuándo escuchar al protocolo, cuándo ejecutar comandos y cuándo detenerse.

## Estados del Sistema
1.  **ESTADO_INICIAL (0):** Arranque.
2.  **ESTADO_ESPERA (1):** Idle. Esperando comandos manuales o inicio de recepción.
3.  **ESTADO_RECIBIENDO (2):** Escuchando activamente al protocolo (handoff a `ProtocoloComunicacion`).
4.  **ESTADO_EJECUTANDO (3):** Procesando la lista de comandos secuencialmente.
5.  **ESTADO_COMPLETADO (4):** Fin de la secuencia.
6.  **ESTADO_ERROR (5):** Estado de fallo.

## Responsabilidades
*   Coordinar `ProtocoloComunicacion` y `EjecucionComandos`.
*   Manejar la transición entre recibir datos y ejecutarlos.
*   Implementar la lógica de ejecución secuencial (Comando 1 -> Esperar fin -> Comando 2...).
*   Evitar condiciones de carrera (Race Conditions) asegurando que solo un proceso controle los actuadores a la vez.

## Funciones Principales

### `actualizar()`
El corazón del sistema. Se llama en cada ciclo del `loop()`.
*   Verifica timeouts.
*   Delega la comunicación al protocolo si está en modo recepción.
*   Si está en modo ejecución, gestiona el avance de la secuencia de comandos.

### `iniciarRecepcion()` / `iniciarEjecucion()`
Transiciones seguras de estado iniciadas por el usuario (o por la GUI).

## Uso en el Sistema
Es la clase de más alto nivel (debajo del `main`). Centraliza la lógica de negocio para que `main_receptor.cpp` sea lo más simple posible.
