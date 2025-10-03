## DECISIÓN: Usar ESP32 WROOM con Arduino Framework

### ALTERNATIVAS CONSIDERADAS:
- Raspberry Pi Pico (menor potencia, sin WiFi)
- ESP32 con ESP-IDF (más complejo)
- Arduino Uno (limitaciones hardware)

### RAZONES ELEGIDAS:
- Potencia suficiente para lógica compleja
- WiFi integrado para futuras expansiones
- Ecosystem Arduino maduro y documentado
- Balance entre rendimiento y desarrollo rápido
- Compatibilidad con PlatformIO

### COMPROMISOS ACEPTADOS:
- Overhead de Arduino vs código bare metal
-  Limitaciones en control de bajo nivel

## DECISIÓN: Arquitectura en 3 capas separadas

### PATRÓN: Separation of Concerns (SoC)

### BENEFICIOS:
- Mantenibilidad: Cambios aislados
- Testabilidad: Cada capa testeable independientemente
- Flexibilidad: Puede cambiar UART por WiFi fácilmente
- Escalabilidad: Añadir sensores sin afectar lógica

EJEMPLO PRÁCTICO:
Si cambiamos UART por MQTT:
- Solo modificar ProcesamientoDatos
- MaquinaEstado y EjecucionComandos NO cambian

## DECISIÓN: Usar FSM (Finite State Machine) para lógica de control

### ALTERNATIVAS:
- Programación lineal (spaghetti code)
- Interrupciones (complejo de debuggear)

### VENTAJAS FSM:
- Comportamiento predecible
- Fácil de entender y documentar
- Manejo robusto de errores
- Transiciones explícitas

### IMPLEMENTACIÓN:
Estados: ESPERA, EJECUCIÓN, RECIBIENDO, ERROR
Transiciones basadas en: datos UART, comandos activos, errores

## DECISIÓN: Usar struct en lugar de Clases para Datos

### RAZONES

- Más simple y eficiente
- Fácil serialización/deserialización
- Compatible con C y C++
- Menos overhead que clase con getters/setters