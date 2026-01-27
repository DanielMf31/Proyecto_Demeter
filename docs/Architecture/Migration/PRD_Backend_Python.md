# Product Requirement Document: Migración Backend Python + GUI

**Estado:** Draft
**Versión:** 1.1.0
**Objetivo:** Backend capaz de gestionar inventario con MACs y orquestar secuencias.

## 1. Arquitectura del Sistema

### 1.1 Cambios en `DeviceManager`
*   El `inventory.json` ahora **DEBE** incluir el campo `mac_address` para cada dispositivo remoto.
*   Al iniciar, el Backend debe iterar el inventario y enviar una ráfaga de `CMD_ROUTE_ADD` al Gateway para configurarlo.

## 2. Estructura de Datos (JSON)

```json
{
  "devices": {
    "bomba_1": {
      "node_id": 10,
      "mac": "FF:FF:FF:FF:FF:FF",
      "pin": 4,
      "type": "RELAY"
    }
  }
}
```

## 3. Requisitos Funcionales

### 3.1 Inicialización del Sistema
1.  Abrir Puerto Serie (Gateway).
2.  Esperar `Ping/Pong` con Gateway.
3.  **Sync Phase:** Enviar configuración de rutas (`ID -> MAC`) por cada dispositivo en JSON.
4.  Ready.

### 3.2 Generación de Secuencias
*   La GUI debe permitir crear "Escenas" o "Rutinas".
*   El Backend debe compilar estas rutinas en un `CMD_SEQUENCE` binario y enviarlo al Gateway.

## 4. Plan de Migración (Fase Python - Prioritaria)
El usuario ha solicitado empezar por aquí.
1.  **Refactorizar `DeviceManager`** para soportar MACs.
2.  **Implementar `protocol_v2.py`** con soporte para paquete `SEQUENCE`.
3.  **Implementar `GatewaySync` logic** (enviar rutas al iniciar).
