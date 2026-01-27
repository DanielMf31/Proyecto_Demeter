# Product Requirement Document: Protocolo Demeter V2 (Definition)

**Estado:** Draft
**Versión:** 2.1.0 (Updated for ESP-NOW & Sequencing)
**Fecha:** 27 Enero 2026

## 1. Introducción
Este documento define el estándar binario para la comunicación Demeter V2. Se añade soporte específico para enrutamiento MAC (ESP-NOW) y ejecución secuencial delegada en el Gateway.

## 2. Especificaciones Técnicas

### 2.1 Estructura del Frame (Trama)
*(Packed, Little Endian)*

| Byte Offset | Campo | Tipo | Descripción |
| :--- | :--- | :--- | :--- |
| 0 | `SYNC` | uint8 | `0xFE` |
| 1 | `LEN` | uint8 | Longitud Payload |
| 2 | `FLAGS` | uint8 | Rit 0: ACK Req. |
| 3 | `SRC_ID` | uint8 | ID Lógico Remitente |
| 4 | `DST_ID` | uint8 | ID Lógico Destinatario |
| 5 | `CMD_ID` | uint8 | Ver Catálogo |
| 6...N | `PAYLOAD`| bytes | Datos |
| N+1 | `CRC` | uint8 | Checksum CRC-8 |

### 2.2 Catálogo de Comandos (Ampliado)

| Hex | Mnemónico | Dirección | Payload | Descripción |
| :--- | :--- | :--- | :--- | :--- |
| **0x01** | `CMD_PING` | Bi-dir | - | Keep-alive. |
| **0x02** | `CMD_ACK` | Bi-dir | - | OK. |
| **0x03** | `CMD_NACK` | Bi-dir | `[Err]` | Error. |
| **0x0A** | `CMD_ROUTE_ADD`| RPi->GW | `[ID][MAC(6)]` | Registra ruta en tabla GW. |
| **0x10** | `CMD_SET_GPIO` | M->N | `[Pin][Val]` | Set Digital directo. |
| **0x30** | `CMD_SEQUENCE` | RPi->GW | `[Count][Steps...]` | Ejecuta lote secuencial con delays. |

### 2.3 Estructura: SequenceStep
Utilizada dentro del payload de `CMD_SEQUENCE`.

| Offset | Campo | Tipo | Desc |
| :--- | :--- | :--- | :--- |
| 0 | `TargetID` | u8 | ID del nodo esclavo |
| 1 | `Command` | u8 | Ej. 0x10 (SET_GPIO) |
| 2 | `Pin` | u8 | GPIO Pin |
| 3 | `Value` | u8 | 1/0 o PWM |
| 4 | `DelayMs` | u32 | Espera POST-ejecución (Little Endian) |
| **Total**| | **8 B** | |

## 3. Lógica de Enrutamiento (Gateway)
*   El Gateway mantiene una `RoutingTable` en RAM (Map: `ID` -> `MAC`).
*   Al recibir un frame con `DST_ID != 0` (y != Self), busca en la tabla.
    *   Si encuentra MAC: Reenvasa y envía por ESP-NOW.
    *   Si no encuentra: Envía `CMD_NACK` (Route Not Found).
