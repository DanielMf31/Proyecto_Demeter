# VISION SISTEMA Y ARQUITECTURA

## PROBLEMA: 
- Control manual ineficiente de sistemas de riego agrícola
- Falta de automatización en secuencias de riego
- Dificultad para monitoreo remoto
- Alto consumo de agua por riego no optimizado

## SOLUCIÓN DEMETER:
Sistema embebido que automatiza el control de bombas de agua mediante
comandos recibidos vía UART desde una Raspberry Pi, con capacidad de
ejecución secuencial y manejo robusto de errores.

## ENTORNO: Invernaderos y sistemas de riego agrícola
ACTORES: 
- Terminal: Envía comandos y consulta logs del sistema
- Raspberry Pi: Orquesta el sistema, envía comandos
- ESP32: Ejecuta comandos en tiempo real
- Sensores: Futura expansión para humedad/temperatura
- Actuadores: Bombas de agua, válvulas

## FLUJO TÍPICO:

1. Terminal envía comandos a Raspberry Pi
2. Raspberry Pi calcula secuencia de riego
3. Envía comandos por UART a ESP32
4. ESP32 ejecuta secuencia automáticamente
5. Sistema reporta estado y errores

## CAPAS DEL SISTEMA

### CAPA 1: COMUNICACION (PROCESAMIENTODATOS)

#### PROPÓSITO: Bridge entre el mundo externo y el sistema interno

#### RESPONSABILIDADES:
- Recepción de datos UART crudos
- Parseo y validación de mensajes
- Conversión a estructuras internas
- Buffering y manejo de overflow

#### INTERFACES:
- Entrada: Serial2 (UART)
- Salida: Estructuras Comando

### CAPA 2: LOGICA DE CONTROL (MAQUINAESTADO)

#### PROPÓSITO: Cerebro del sistema - orquesta el comportamiento

#### RESPONSABILIDADES:
- Gestión de estados del sistema
- Transiciones entre modos operación
- Secuenciación de comandos
- Manejo de condiciones de error

#### INTERFACES:
- Entrada: Estado de datos y hardware
- Salida: Decisiones de ejecución

### CAPA 3: EJECUCION (EJECUCIONCOMANDOS)

#### PROPÓSITO: Ejecutor físico - interactúa con el mundo real

#### RESPONSABILIDADES:
- Control directo de GPIO
- Temporización de actuadores
- Safety checks
- Reporte de estado ejecución

#### INTERFACES:
- Entrada: Comandos validados
- Salida: Señales GPIO

