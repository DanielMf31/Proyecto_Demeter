# Análisis Detallado de Pruebas: ProtocolEngine

**Archivo Analizado:** `src/core/ProtocolEngine.cpp` y `include/core/ProtocolEngine.h`
**Responsabilidad:** Capa de enlance de datos y transporte. Maneja la serialización, deserialización, integridad (CRC) y despacho de comandos.

## 1. Fundamentos del Testing (Por qué testeamos esto)

La robustez del `ProtocolEngine` es no negociable. Un fallo aquí implica que un nodo quede incomunicado o ejecute acciones erróneas.

### 1.1. Frame Integrity (Integridad de Trama)
**Objetivo:** Asegurar que lo que entra es exactamente lo que se envió.
**Riesgo:** Ruido eléctrico o errores de transmisión pueden alterar bits. Si aceptamos una trama corrupta, podríamos encender un motor por error.
**Test:** Validar Sync Byte, Longitud y, sobre todo, **CRC (Cyclic Redundancy Check)**.

### 1.2. Command Dispatch (Despacho de Comandos)
**Objetivo:** Asegurar que el Byte de Comando (`CMD_ID`) active la función lógica correcta.
**Riesgo:** Un error "off-by-one" en un `switch/case` podría hacer que un `PING` se interprete como un `RESET`.
**Test:** Barrido exhaustivo de **TODOS** los Command IDs definidos.

### 1.3. Serialization (Serialización)
**Objetivo:** Asegurar que al convertir datos (float, int) a bytes, se respeta el formato (Endianness, Scaling).
**Riesgo:** Si el Gateway espera Little Endian y enviamos Big Endian, una temperatura de 25.0°C podría leerse como 6000°C.
**Test:** Verificar byte a byte la salida de `sendFrame`.

---

## 2. Matriz de Pruebas Exhaustiva (Test Matrix)

A continuación se detallan los tests necesarios para cubrir el 100% de la especificación del protocolo V2.

### Grupo A: Integridad del Protocolo (Protocol Core)

| ID | Nombre del Test | Entrada | Comportamiento Esperado | Razón Crítica |
| :--- | :--- | :--- | :--- | :--- |
| **PC01** | `test_reject_invalid_sync` | Byte inicial `0xAA` (No `0xFE`) | Descarte silencioso. No callbacks. | Evita sincronización falsa con ruido. |
| **PC02** | `test_reject_short_header` | Trama incompleta (< 6 bytes) | Descarte por *underflow*. | Previene lecturas de memoria inválida (SegFault). |
| **PC03** | `test_reject_crc_mismatch` | Trama con Payload modificado pero CRC original | Descarte por error de CRC. | Evita ejecución de comandos corruptos. |
| **PC04** | `test_routing_ignore_foreign` | Trama con `DST_ID != MyID` | Descarte lógico (o Forwarding si es Gateway). | Seguridad y eficiencia de red. |
| **PC05** | `test_accept_broadcast` | Trama con `DST_ID == 0xFF` | Aceptación y procesado. | Necesario para descubrimiento y alertas globales. |

### Grupo B: Comandos de Control (Control Commands)

| ID | Cmd ID | Test de Parsing (Rx) | Test de Serialización (Tx) | Detalle de Implementación |
| :--- | :--- | :--- | :--- | :--- |
| **CC01** | `0x01` PING | Inyectar `PING`. Verificar envío automático de `ACK`. | Llamar `sendPing()`. Verificar bytes `[01]` en payload. | El "latido" del sistema. Vital para diagnósticos. |
| **CC02** | `0x02` ACK | Inyectar `ACK`. Verificar callback `onAckRecv`. | Llamar `sendAck()`. Verificar bytes `[02]`. | Confirmación de recepción. Sin esto, habrá reintentos infinitos. |
| **CC03** | `0x03` NACK | Inyectar `NACK`. Verificar callback (si existe). | Llamar `sendNack()`. Verificar bytes `[03]`. | Feedback de error explícito. |
| **CC04** | `0x0A` ROUTE | Inyectar `ROUTE_ADD` con ID+MAC. Verificar llamada a `strategy->registerRoute`. | (No suele enviarse desde nodo, solo Rx). | Permite al Gateway aprender topología dinámica. |
| **CC05** | `0x0D` SYS | Inyectar `SYSTEM_REPORT`. Verificar Mode/Batt. | Llamar `sendSystemReport`. Verificar Endianness de batería (`uint16`). | Monitoreo de salud del nodo. |
| **CC06** | `0x20` GET_S | Inyectar `GET_SENSORS`. Verificar callback. | (No implementado Tx en nodo). | Interactividad bajo demanda. |

### Grupo C: Comandos de Actuación (Actuation)

| ID | Cmd ID | Test de Parsing (Rx) | Test de Serialización (Tx) | Detalle de Implementación |
| :--- | :--- | :--- | :--- | :--- |
| **AC01** | `0x10` GPIO | Inyectar `SET_GPIO` `[PIN, VAL, FLG]`. Verificar `cmd.pin`, `cmd.value`. | Llamar `sendSetGpio`. Verificar `payload[1]` como booleano (0/1). | **CRÍTICO:** Control básico de relés. Verificar conversión `bool -> uint8`. |
| **AC02** | `0x11` PWM | Inyectar `SET_PWM` `[PIN, VAL_L, VAL_H]`. Verificar reconstrucción `uint16`. | (Tx no común en nodo). | Control de motores/dimmers. Verificar Little Endian. |
| **AC03** | `0x30` SEQ | Inyectar secuencia de 3 pasos. Verificar vector `steps` tamaño 3 y datos correctos. | (Tx no común en nodo). | Automatización compleja. Verificar parsing de array variable. |

### Grupo D: Reporte de Datos (Telemetry)

| ID | Cmd ID | Test de Parsing (Rx) | Test de Serialización (Tx) | Detalle de Implementación |
| :--- | :--- | :--- | :--- | :--- |
| **DT01** | `0x0B` T/H | Inyectar `TEMP_HUM` `[T_L, T_H, H_L, H_H]`. Verificar float `25.43` recuperado. | Llamar `sendTempHumReport(25.43, ...)`. Verificar `2543` en bytes. | **CRÍTICO:** Precisión de datos. Validar factor de escala x100. |
| **DT02** | `0x0C` PIN | Inyectar `PIN_REPORT`. Verificar pin y estado. | Llamar `sendPinReport`. Verificar payload. | Feedback de actuación. Confirma que la luz se encendió. |

---

## 3. Guía de Errores Comunes de Implementación

Al escribir estos tests, busca activamente estos fallos:

1.  **Endianness Invertido:** Enviar `0x0102` (258) y recibir `0x0201` (513). *Solución:* Usar operaciones bitwise explícitas (`>> 8`), nunca `memcpy` directo de structs multi-byte.
2.  **Padding de Structs:** Si usas `struct` para mapear el payload, el compilador puede añadir bytes de relleno. *Solución:* Usar `__attribute__((packed))` o serializar byte a byte (preferido).
3.  **Signo en Temperaturas:** ¿Qué pasa con -5.0°C? *Solución:* Verificar que el casteo a `int16_t` maneja el signo correctamente (complemento a 2).

---

Este documento debe servir como "Checklist de Calidad" antes de dar por finalizado el módulo `ProtocolEngine`.
