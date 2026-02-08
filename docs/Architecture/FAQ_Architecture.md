# Preguntas de Repaso Diario: Arquitectura del Sistema

Usa este documento cada mañana para verificar que tu modelo mental del sistema sigue intacto.

## Nivel 1: Conceptos Básicos

1.  **¿Quién es responsable de validar que los datos no estén corruptos?**
    *   *Respuesta:* `ProtocolEngine` (vía CRC).
2.  **¿Quién decide si un comando se ejecuta ahora o se guarda en una cola?**
    *   *Respuesta:* `SystemContext` (basado en `_execMode`).
3.  **¿Sabe el `ProtocolEngine` qué es un LED o un Motor?**
    *   *Respuesta:* No. Es "ciego" al hardware. Solo sabe disparar eventos.

## Nivel 2: Flujo de Datos

4.  **Si cambio el medio de comunicación de UART a WiFi, ¿tengo que cambiar el código de `ProtocolEngine`?**
    *   *Respuesta:* No. `ProtocolEngine` recibe un `IComms*`. Si le das una `WifiStrategy`, seguirá funcionando igual.
5.  **¿Por qué pasamos `const SetGpioCmd&` y no `SetGpioCmd` por valor?**
    *   *Respuesta:* Para evitar copiar datos innecesariamente (Eficiencia / Zero-Copy).

## Nivel 3: Casos Límite

6.  **Si el `SystemContext` está en modo `ERROR`, ¿qué pasa cuando llega un comando válido por UART?**
    *   *Respuesta:* El `ProtocolEngine` lo procesa y llama al callback, pero el `SystemContext` (dentro de su función `handle...`) lo descarta inmediatamente al ver el estado de error.
7.  **¿Qué pasa si el CRC falla?**
    *   *Respuesta:* `ProtocolEngine` descarta la trama silenciosamente (o incrementa un contador de errores) y NO llama a ningún callback. El `SystemContext` ni se entera.

## Ejercicio Mental Diario
*   *"Imagina que eres un byte `0x10` (Comando GPIO) entrando por el cable. Describe tu viaje paso a paso hasta que el LED se enciende."*
