## ESTADO_ESPERA (Estado Inicial)
CONDICIÓN ENTRADA: Sistema booteado o comandos completados
COMPORTAMIENTO:
- Apagar todos los actuadores
- Monitorear UART para nuevos comandos
- Bajo consumo energético
POSIBLE SALIDA: → RECIBIENDO (si hay datos UART)

## ESTADO_EJECUCIÓN (Estado Activo)  
CONDICIÓN ENTRADA: Comandos pendientes por ejecutar
COMPORTAMIENTO:
- Ejecutar secuencia actual de comandos
- Controlar temporizaciones
- Monitorear finalización
POSIBLE SALIDA: → ESPERA (si secuencia completa)

## ESTADO_RECIBIENDO (Estado de Entrada)
CONDICIÓN ENTRADA: Datos disponibles en buffer UART
COMPORTAMIENTO:
- Leer y parsear mensajes UART
- Validar y almacenar comandos
- Preparar siguiente ejecución
POSIBLE SALIDA: → EJECUCIÓN (si comandos válidos)

## ESTADO_ERROR (Estado de Seguridad)
CONDICIÓN ENTRADA: Timeout, error hardware, datos inválidos
COMPORTAMIENTO:
- Apagar todos los actuadores (fail-safe)
- Reportar error via Serial
- Esperar reset manual
POSIBLE SALIDA: → ESPERA (solo por reset)

# CONSIDERACIONES DE SEGURIDAD

## FAIL-SAFE Design:
- ESTADO_ERROR apaga TODOS los actuadores inmediatamente
- Timeouts en todas las operaciones bloqueantes
- Verificación de rangos en todos los parámetros
- Recovery manual requerido desde ESTADO_ERROR

## DETERMINISMO:
- Mismas entradas → mismos estados
- Sin dependencias de timing crítico
- Estados bien definidos y mutuamente excluyentes