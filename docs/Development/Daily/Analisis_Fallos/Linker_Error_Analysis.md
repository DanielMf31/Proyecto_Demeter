# Análisis del Error de Compilación (Linker)

## Descripción del Problema
El compilador (linker) reporta que no encuentra las definiciones para dos métodos en `SystemManager`:

1. `SystemManager::handleGpioCommand(Demeter::SetGpioCmd const&)`
2. `SystemManager::handleExecSequence(Demeter::ExecSequenceCmd const&)`

**Error Log:**
```
undefined reference to `SystemManager::handleGpioCommand(Demeter::SetGpioCmd const&)'
undefined reference to `SystemManager::handleExecSequence(Demeter::ExecSequenceCmd const&)'
```

## Causa Raíz
Se actualizaron las firmas en el archivo de cabecera (`SystemManager.h`) para aceptar las nuevas estructuras `Demeter::SetGpioCmd` y `Demeter::ExecSequenceCmd`, pero **no se actualizaron las implementaciones correspondientes en el archivo fuente (`SystemManager.cpp`)**.

Es probable que `SystemManager.cpp` todavía tenga las implementaciones antiguas o simplemente falten las nuevas.

## Solución Propuesta

### 1. Implementar `handleGpioCommand`
En `src/core/SystemManager.cpp`, añadir o actualizar:

```cpp
void SystemManager::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_executor) {
        // Ejecución inmediata o agregar a cola según el modo
        if (_execMode == ExecutionMode::IMMEDIATE) {
            _executor->setPin(cmd.pin, cmd.value);
            // Opcional: Enviar PinReport de vuelta
            sendPinStatus(cmd.sourceId, {0, cmd.pin, cmd.value}); // Asumiendo sourceId en cmd o contexto
        } else {
            _commandQueue.push_back(cmd);
        }
    }
}
```

### 2. Implementar `handleExecSequence`
En `src/core/SystemManager.cpp`, añadir o actualizar:

```cpp
void SystemManager::handleExecSequence(const Demeter::ExecSequenceCmd& cmd) {
    // Lógica para iniciar la secuencia
    _activeSequence = cmd.steps;
    _sequenceStepIndex = 0;
    _isSequencerActive = true;
    _lastStepTime = millis();
    // Ejecutar primer paso inmediatamente o esperar
}
```

## Próximos Pasos
Voy a proceder a aplicar estas correcciones en `SystemManager.cpp` para resolver los errores de enlace y permitir que los tests compilen correctamente.
