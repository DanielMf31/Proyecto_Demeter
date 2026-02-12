# 2. Módulos Principales (Core Modules)

Los módulos principales contienen la lógica de negocio y de control de flujo, independientes del hardware específico.

## 2.1 Protocol Engine (`ProtocolEngine.h/cpp`)

El motor del protocolo es el responsable de interpretar los bytes crudos y convertirlos en comandos estructurados.

### Funciones Clave
*   **Deserialización:** Lee bytes del buffer de entrada. Busca el byte de sincronización `SYNC (0xFE)` y reconstruye la trama.
*   **Validación:**
    1.  Verifica `SYNC`.
    2.  Verifica longitud de payload.
    3.  Calcula y valida CRC-8 (Suma Modular % 256).
*   **Despacho:** Si la trama es válida y para este nodo (o broadcast), invoca el *callback* registrado para ese comando.
*   **Serialización:** Construye tramas de respuesta (ACK, NACK, DATA_REPORT) con cabeceras y CRC correctos.

### Uso
```cpp
// 1. Instanciación con Estrategia de Comunicación
ProtocolEngine engine(&myStrategy);

// 2. Registro de Callbacks
engine.onSetGpio([](const Demeter::SetGpioCmd& cmd) {
    // Acción al recibir comando GPIO
});

// 3. Loop de actualización
void loop() {
    engine.update(); // Lee bytes y procesa
}
```

## 2.2 System Context (`SystemContext.h/cpp`)

El contexto del sistema actúa como el **Controlador** en un esquema MVC. Orquesta la interacción entre el Protocolo (Vista/Entrada) y el Hardware (Modelo/Salida).

### Responsabilidades
1.  **Gestión de Estado:** Mantiene el estado global del sistema (`BOOT`, `IDLE`, `PROCESSING`, `ERROR`).
2.  **Modos de Ejecución:**
    *   **Inmediato (`IMMEDIATE`):** Los comandos se ejecutan tan pronto llegan. (Probado y funcional).
    *   **En Cola (`INTERACTIVE_QUEUE`):** Los comandos se almacenan en un buffer y se ejecutan solo bajo demanda (comando `EXECUTE_QUEUE` o gatillo manual). Útil para sincronizar acciones complejas.
3.  **Secuenciador:** Maneja la ejecución temporal de listas de pasos (`EXEC_SEQUENCE`). Permite definir retardos entre acciones sin bloquear el `loop()` principal (usando `millis()`).

### Flujo de Ejecución (Secuencia Típica)

1.  `ProtocolEngine` recibe bytes -> Valida -> Llama `callback`.
2.  `SystemContext::handleGpioCommand` recibe el comando estructurado.
3.  Si modo es `IMMEDIATE`:
    *   Cambia estado a `PROCESSING`.
    *   Llama a `GpioController::execute(cmd)`.
    *   Regresa estado a `IDLE`.
4.  Si modo es `QUEUE`:
    *   Empuja comando al `std::vector<SetGpioCmd> _commandQueue`.
