# Arquitectura de SystemContext en Demeter Firmware

Este documento detalla la propuesta de implementación del componente `SystemContext`, diseado para centralizar el estado, la identidad y la configuración del nodo dentro de la arquitectura del firmware.

## 1. Objetivo
Desacoplar la **Data (Estado/Configuración)** de la **Lógica (SystemManager)** y la **Comunicación (ProtocolEngine)**. `SystemContext` actuará como la "Fuente de la Verdad" para todo el sistema.

## 2. Estructura de SystemContext

`SystemContext` no será solo un struct de datos, sino una clase gestora que encapsula:
1.  **Identidad del Nodo**: Quién soy (ID, MAC, Rol).
2.  **Estado Operativo**: En qué estado estoy (BOOT, RUNNING, ERROR, SLEEP).
3.  **Configuración**: Capacidades activas (Sensores, Actuadores, Deep Sleep).
4.  **Estado de Red**: Quién es mi Gateway, métricas de conexión.

### Definición Propuesta (`include/core/SystemContext.h`)

```cpp
#pragma once
#include <stdint.h>
#include "InternalTypes.h"
#include <vector>

namespace Demeter {

    // Roles del Nodo
    enum class NodeRole {
        SENSOR,
        ACTUATOR,
        GATEWAY,
        HYBRID
    };

    /**
     * @brief Clase centralizada para el Contexto del Sistema.
     */
    class SystemContext {
    private:
        // --- Identity ---
        uint8_t _nodeId;
        uint8_t _gatewayId;
        NodeRole _role;
        
        // --- State ---
        SystemState _currentState; // Definido en InternalTypes o SystemManager
        uint16_t _batteryMv;
        uint32_t _uptimeSeconds;
        uint8_t _lastErrorCode;

        // --- Configuration ---
        bool _deepSleepEnabled;
        uint32_t _reportIntervalMs;
        std::vector<uint8_t> _activePins;

    public:
        SystemContext();

        // Getters & Setters
        void setIdentity(uint8_t id, NodeRole role, uint8_t gatewayId = 1);
        uint8_t nodeId() const { return _nodeId; }
        uint8_t gatewayId() const { return _gatewayId; }
        NodeRole role() const { return _role; }

        // State Management
        void setState(SystemState state);
        SystemState getState() const { return _currentState; }
        
        void updateBattery(uint16_t mv);
        uint16_t getBattery() const { return _batteryMv; }

        // Config
        void setConfig(uint32_t intervalMs, bool deepSleep);
        bool isDeepSleepEnabled() const { return _deepSleepEnabled; }
    };
}
```

## 3. Integración en la Arquitectura

### A. SystemManager como Consumidor
`SystemManager` dejará de tener variables sueltas como `_state` o configuraciones dispersas. En su lugar, poseerá una instancia de `SystemContext`.

**SystemManager.h (Refactorizado):**
```cpp
class SystemManager {
private:
    Demeter::SystemContext _context; // Instancia propia o recibida
    ProtocolEngine* _engine;
    // ...
public:
    // ...
    Demeter::SystemContext& getContext() { return _context; }
};
```

### B. Node_* como Configuradores
Las clases de alto nivel (`Node_Sensor`, `Node_Actuator`) serán las encargadas de **inicializar** el Contexto durante el `begin()`.

**Ejemplo en Node_Sensor::begin():**
```cpp
void Node_Sensor::begin() {
    // 1. Configurar Contexto
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::SENSOR);
    ctx.setConfig(_reportIntervalMs, _deepSleepEnabled);

    // 2. Setup Normal
    _systemManager->setup();
}
```

## 4. Funcionalidades Clave

### 1. Persistencia de Estado (Futuro)
Al tener todo el estado en un solo objeto `SystemContext`, será trivial guardar/cargar este objeto en la EEPROM o Flash para recuperar el estado tras un reinicio o Deep Sleep.

### 2. Reportes de Sistema Simplificados
Generar un `SystemReport` será directo:
```cpp
void SystemManager::broadcastSystemReport() {
    Demeter::SystemReport report;
    report.sourceId = _context.nodeId();
    report.mode = (uint8_t)_context.getState();
    report.batteryMv = _context.getBattery();
    
    sendSystemStatus(_context.gatewayId(), report); // Enviar al Gateway configurado
}
```

### 3. Toma de Decisiones Centralizada
El `SystemManager` consultará el contexto para decidir:
- "¿Debo dormir ahora?" -> `_context.isDeepSleepEnabled()`
- "¿A quién envío esto?" -> `_context.gatewayId()`

## 5. Ruta de Implementación

1.  **Crear `InternalTypes` o `SystemTypes`**: Mover `SystemState` a un lugar común accesible por Contexto.
2.  **Implementar `SystemContext`**: Crear la clase en `src/core/SystemContext.cpp`.
3.  **Refactorizar `SystemManager`**:
    - Incluir `SystemContext`.
    - Reemplazar variables locales (`_state`, etc.) por llamadas a `_context`.
4.  **Actualizar `Node_*`**: Configurar el contexto en el arranque.
5.  **Tests Unitarios**: Probar `SystemContext` aisladamente y luego dentro de `SystemManager`.
