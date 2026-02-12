# Diseño Arquitectónico: Firmware C++ (ESP32)

**Versión:** 2.1 (Implementado)
**Filosofía:** Clean Architecture / SOLID
**Patrón Principal:** Strategy Pattern para Comunicaciones.

## 1. Visión General
El sistema desacopla el **Protocolo** (Lógica) del **Transporte** (Física) y de la **Ejecución**.

### Flujo de Datos
`[Bytes UART]` -> `UartStrategy` -> `ProtocolEngine` -> `[SetGpioCmd Struct]` -> `GpioController` -> `[Hardware PIN]`

---

## 2. API Implementada

### 2.1 Core: `ProtocolEngine`
El cerebro del sistema de comunicaciones.
*   **Responsabilidad:** Parser Binario y Validación CRC.
*   **Ubicación:** `src/core/ProtocolEngine.cpp`

```cpp
// Uso en main.cpp
ProtocolEngine engine(&uartStrategy);

// Configurar Callback
engine.onSetGpio([](const Demeter::SetGpioCmd& cmd) {
    gpioController.execute(cmd);
});

// En el loop principal
engine.update();
```

### 2.2 Core: `GpioController`
El ejecutor de acciones físicas.
*   **Responsabilidad:** Abstraer `digitalWrite` y validar pines seguros.
*   **Ubicación:** `src/core/GpioController.cpp`

```cpp
Demeter::SetGpioCmd cmd = {4, true, 0};
controller.execute(cmd); // Enciende GPIO 4
```

### 2.3 System: `SystemContext`
El orquestador del flujo de trabajo y la máquina de estados.
*   **Responsabilidad:** Unificar Protocolo y Hardware. Gestionar modos (Inmediato/Cola) y **Secuencias**.
*   **Ubicación:** `src/core/SystemContext.cpp`
*   **Features:**
    *   **Ejecución de Secuencias:** Implementa un motor no bloqueante basado en `millis()` para ejecutar `ExecSequenceCmd`.

### 2.4 Tipos Internos (`InternalTypes.h`)
El "Lenguaje Común" del sistema.
```cpp
struct SetGpioCmd {
    uint8_t pin;
    bool value;
    uint8_t flags;
};
```

---

## 3. Pruebas Unitarias (Native)
El sistema es 100% testeable en PC gracias a Mocks.

| Test Suite | Cobertura | Comando |
| :--- | :--- | :--- |
| `test_native_comms` | Valida `UartStrategy` (Send/Read/Mock). | `pio test -e native -f test_native_comms` |
| `test_native_full` | Valida Flujo Completo: Bytes -> Callback -> Ejecución. | `pio test -e native -f test_native_full` |

## 4. Guía de Extensión
Para añadir un nuevo comando (ej. `SET_PWM`):
1.  Definir `struct SetPwmCmd` en `InternalTypes.h`.
2.  Añadir caso `CMD_SET_PWM` en `ProtocolEngine::parseFrame`.
3.  Implementar `GpioController::executePwm`.
4.  Conectar en `main.cpp`.
