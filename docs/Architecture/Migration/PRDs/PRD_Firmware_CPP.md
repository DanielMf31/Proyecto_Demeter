# Product Requirement Document: Migración Firmware ESP32 (C++)

**Estado:** Draft
**Versión:** 1.1.0
**Objetivo:** Firmware híbrido (Nodo/Gateway) con soporte ESP-NOW y Secuenciador.

## 1. Arquitectura de Software

### 1.1 Nuevos Módulos Requeridos
Además de Protocol y Hardware, se añaden servicios de red y lógica.

*   **`NetworkManager`:** Maneja `ESPNOW` y la `RoutingTable`.
*   **`SequenceExecutor`:** Motor asíncrono que procesa listas de tareas. No debe usar `delay()` bloqueante, sino `millis()`.

## 2. Estructura de Carpetas

```text
C++ /
├── include /
│   ├── logic /  <-- NUEVO
│   │   ├── SequenceExecutor.h
│   │   └── RouteTable.h
│   ├── transport /
│   │   ├── EspNowTransport.h  <-- NUEVO
│   │   └── UartTransport.h
...
```

## 3. Requisitos Funcionales

### 3.1 `RouteTable` (Gateway Mode)
*   Estructura simple: `struct Tuple { uint8_t id; uint8_t mac[6]; }`.
*   Array estático o `std::map` (preferible array simple para evitar fragmentación heap).
*   Comando `CMD_ROUTE_ADD` rellena esta tabla.

### 3.2 `SequenceExecutor`
*   Recibe un payload de `CMD_SEQUENCE`.
*   Estado: `IDLE`, `EXECUTING`, `WAITING_DELAY`.
*   **Lógica:**
    1.  Parsea paso N.
    2.  Invoca `ProtocolEngine::send(TargetID, CMD...)`.
    3.  Espera ACK del Target (Timeout 1s).
    4.  Si ACK OK: Entra en estado `WAITING_DELAY` por `post_delay` ms.
    5.  Al terminar delay: N++. Repetir.

### 3.3 Gestión de Errores en Secuencia
*   Si un nodo no responde (timeout ACK), la secuencia debe abortar y reportar error a RPi: `CMD_NACK` con índice del paso fallido.

## 4. Plan de Migración (Fase C++)
Prioridad ESP-NOW.
1.  Implementar `EspNowTransport`.
2.  Implementar `RouteTable` y lógica de reenvío.
3.  Implementar `SequenceExecutor`.
