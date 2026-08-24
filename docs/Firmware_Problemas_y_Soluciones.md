# Firmware Demeter — Problemas que Resuelve y Cómo los Implementa

Este documento cataloga **todos los problemas técnicos** que el firmware ESP32 resuelve, agrupados por categoría. Para cada uno se explica el **concepto teórico** y la **implementación concreta** en el código.

---

## Índice

1. [Abstracción del Medio de Comunicación](#1-abstracción-del-medio-de-comunicación)
2. [Protocolo Binario Fiable](#2-protocolo-binario-fiable)
3. [Establecimiento de Conexión (Handshake)](#3-establecimiento-de-conexión-handshake)
4. [Enrutamiento Multi-Interfaz](#4-enrutamiento-multi-interfaz)
5. [Control Seguro de Hardware (GPIO)](#5-control-seguro-de-hardware-gpio)
6. [Abstracción de Sensores](#6-abstracción-de-sensores)
7. [Ejecución No Bloqueante](#7-ejecución-no-bloqueante)
8. [Especialización de Nodos](#8-especialización-de-nodos)
9. [Orquestación de Secuencias](#9-orquestación-de-secuencias)
10. [Testabilidad sin Hardware](#10-testabilidad-sin-hardware)
11. [Compilación Selectiva](#11-compilación-selectiva)
12. [Resiliencia en ISR y Buffers](#12-resiliencia-en-isr-y-buffers)

---

## 1. Abstracción del Medio de Comunicación

### Problema 1.1: Soportar múltiples medios físicos (UART, ESP-NOW) sin cambiar la lógica del protocolo

**Problema:** El Gateway necesita UART (hacia la Raspberry) y ESP-NOW (hacia los nodos mesh). Los nodos sensor/actuador solo usan ESP-NOW. Si la lógica del protocolo está acoplada al medio físico, hay que duplicar código por cada transporte.

**Concepto:** Strategy Pattern (GoF) — definir una interfaz abstracta para el transporte y crear implementaciones intercambiables.

**Implementación:**
- `IComms.h` — Interfaz abstracta con métodos: `begin()`, `send(data, len)`, `available()`, `read()`, `registerRoute(id, mac)`
- `UartStrategy.cpp` — Implementación para UART serial (HardwareSerial de Arduino). `read()` drena agresivamente el buffer FIFO en un vector.
- `EspNowStrategy.cpp` — Implementación para ESP-NOW P2P. Gestiona WiFi STA mode + tabla de rutas (Node ID → MAC address). Callbacks estáticos `onDataSent()` y `onDataRecv()`.
- `ProtocolEngine` recibe un `IComms*` en su constructor — nunca sabe qué medio físico usa.

```cpp
// ProtocolEngine no sabe si envía por UART o ESP-NOW
class ProtocolEngine {
    IComms* _strategy;  // Inyectado en constructor
    void sendFrame(uint8_t target, uint8_t cmd, const uint8_t* payload, uint8_t len);
};
```

### Problema 1.2: Registrar peers ESP-NOW dinámicamente

**Problema:** ESP-NOW requiere que los peers (nodos destino) estén registrados con su dirección MAC antes de poder enviar. Si se hardcodea, no escala.

**Concepto:** Tabla de rutas dinámica — mapeo Node ID → MAC address, con auto-learning desde tramas recibidas.

**Implementación:**
- `EspNowStrategy.cpp` — `registerRoute(nodeId, mac)` almacena el mapeo en un `std::map<uint8_t, mac_array>`
- `onDataRecv()` (callback ISR) — extrae la MAC del emisor y auto-registra el peer si no existe
- `send()` — busca la MAC en la tabla de rutas por destino ID; si no existe, silently drops
- `main_gateway.cpp` — pre-registra las MACs conocidas al arrancar como bootstrap

---

## 2. Protocolo Binario Fiable

### Problema 2.1: Transmitir datos estructurados en un canal serie con mínimo overhead

**Problema:** UART es un stream de bytes sin delimitación de mensajes. Se necesita un formato que permita detectar inicio de trama, longitud, tipo de comando, y verificar integridad — con el mínimo de bytes para no saturar el bus a 115200 baud.

**Concepto:** Protocolo binario con framing — byte de sincronización, campo de longitud, y CRC para integridad.

**Implementación — Frame format:**
```
[SYNC:0xFE] [LEN] [FLAGS] [SRC_ID] [DST_ID] [CMD_ID] [PAYLOAD (LEN bytes)] [CRC]
   1 byte   1 byte 1 byte  1 byte   1 byte   1 byte      variable          1 byte
```

- `ProtocolEngine.cpp` — `sendFrame()`:
  1. Empaqueta header como struct de 6 bytes (`reinterpret_cast` — zero-copy)
  2. Serializa payload según tipo de comando (e.g., SetGpio → `[pin, value, flags]`)
  3. Calcula CRC: `sum(bytes[1..payload]) % 256` (módulo 256)
  4. Concatena: sync + header + payload + CRC
  5. Llama `_strategy->send(buffer, totalLen)`

### Problema 2.2: Detectar tramas corruptas antes de procesarlas

**Problema:** El medio serie es ruidoso (interferencias, baudrate mismatches). Procesar datos corruptos puede causar comportamiento impredecible en actuadores.

**Concepto:** CRC (Cyclic Redundancy Check) — el emisor calcula un checksum y lo añade al final; el receptor recalcula y compara. Si no coincide, descarta.

**Implementación:**
- `ProtocolEngine.cpp` — `parseFrame()`:
  1. Verifica byte sync (0xFE) — fail-fast si no coincide
  2. Verifica longitud declarada vs bytes recibidos
  3. Calcula CRC sobre `[LEN..PAYLOAD]` y compara con último byte
  4. Si falla → descarta la trama entera y retorna sin procesar

```cpp
uint8_t computedCRC = 0;
for (int i = 1; i < headerSize + payloadLen; i++)
    computedCRC += frame[i];
if (computedCRC != frame[totalLen - 1]) return; // Discard
```

### Problema 2.3: Serializar floats en 2 bytes (precisión fija)

**Problema:** Un float en C++ ocupa 4 bytes. Para telemetría con precisión de 0.01 (suficiente para °C y %), se puede reducir a 2 bytes — 50% de ahorro en payload.

**Concepto:** Fixed-point encoding — multiplicar el valor por 100, transmitir como int16 (signed short), dividir por 100 al recibir.

**Implementación:**
- `ProtocolEngine.cpp` — Serialización TempHum:
  ```cpp
  int16_t tempScaled = (int16_t)(report.temperature * 100);
  int16_t humScaled  = (int16_t)(report.humidity * 100);
  // 4 bytes total en vez de 8
  ```
- `demeter_protocol.py` (Python) — Deserialización:
  ```python
  temp_raw, hum_raw = struct.unpack('<hh', payload[:4])
  temperature = temp_raw / 100.0  # Precisión ±0.01°C
  humidity = hum_raw / 100.0
  ```

### Problema 2.4: Despachar comandos heterogéneos desde un solo parser

**Problema:** Una trama puede ser SET_GPIO, PING, TEMP_HUM_REPORT, EXEC_SEQUENCE... cada uno con payload diferente. Un `switch` gigante es difícil de mantener.

**Concepto:** Dispatch por Command ID — el campo `CMD_ID` del header determina cómo interpretar el payload. En C++ se usa switch (optimizado por el compilador a jump table).

**Implementación:**
- `ProtocolEngine.cpp` — `parseFrame()` contiene un `switch(cmdId)` con cases para cada `CommandType`:
  - `SET_GPIO (0x10)` → parsea `[pin, value, flags]`, invoca `_onSetGpioCallback`
  - `TEMP_HUM_REPORT (0x0B)` → parsea `[temp×100, hum×100]`, invoca `_onTempHumCallback`
  - `SENSOR_CLUSTER_REPORT (0x0E)` → parsea `[count, entries...]`, invoca callback
  - `EXEC_SEQUENCE (0x30)` → parsea `[count, steps...]`, invoca `_onExecSequenceCallback`
- Cada comando tiene su callback registrable (`std::function`), permitiendo que SystemManager reaccione sin acoplamiento

---

## 3. Establecimiento de Conexión (Handshake)

### Problema 3.1: Verificar que un nodo está vivo y sincronizado antes de operar

**Problema:** Si un nodo sensor empieza a transmitir sin confirmar que el Gateway está escuchando, los datos se pierden silenciosamente. Se necesita un mecanismo de "presentación" mutua.

**Concepto:** Three-way handshake (inspirado en TCP) — SYN → SYN-ACK → ACK. Garantiza que ambos extremos están activos y preparados.

**Implementación:**
- `SystemManager.cpp` — Máquina de estados:
  ```
  BOOT → initiateHandshake(targetId)
       → HANDSHAKE_SEND_SYN [envía SYN]
       → HANDSHAKE_WAIT_SYN_ACK [espera respuesta]
            ├── Recibe SYN_ACK → envía ACK → RUNNING
            └── Timeout 2s × 3 intentos → ERROR
  ```
- `InternalTypes.h` — `SystemState` enum con 7 estados: BOOT, HANDSHAKE_SEND_SYN, HANDSHAKE_WAIT_SYN_ACK, HANDSHAKE_SEND_ACK, IDLE, RUNNING, ERROR
- `runHandshakeLogic()` — Polling no-bloqueante: comprueba `millis()` vs timeout, reintenta si expira, máximo 3 intentos

### Problema 3.2: Contexto semántico en handshakes

**Problema:** Un ACK genérico no dice para qué es. Se necesita distinguir un ACK de handshake de un ACK de comando.

**Concepto:** Session Context — campo adicional que etiqueta el propósito del handshake/ACK.

**Implementación:**
- `InternalTypes.h` — `SessionContext` enum: GENERAL, SENSOR_REPORT, COMMAND, CRITICAL_ALERT
- El campo `context` viaja en SYN/SYN_ACK/ACK como parte del payload
- El receptor puede decidir qué hacer según el contexto (e.g., priorizar CRITICAL_ALERT)

---

## 4. Enrutamiento Multi-Interfaz

### Problema 4.1: El Gateway debe ser un puente entre UART (Raspberry) y ESP-NOW (mesh)

**Problema:** Un comando que llega de la Raspberry por UART debe reenviarse por ESP-NOW al nodo correcto. Telemetría que llega por ESP-NOW debe reenviarse por UART a la Raspberry. El Gateway no puede tener dos ProtocolEngines.

**Concepto:** Composite Pattern — una estrategia compuesta que agrupa dos estrategias y enruta según el destino.

**Implementación:**
- `GatewayStrategy.cpp` — Implementa `IComms` pero internamente tiene un `UartStrategy*` y un `EspNowStrategy*`
- `send(target, data, len)`:
  - `target_id == 0` → envía por UART (host/Raspberry)
  - `target_id == 1-254` → envía por ESP-NOW (nodos mesh)
  - Broadcast → envía por AMBAS interfaces simultáneamente
- `available()` / `read()` → prioriza UART (baja latencia con host), luego ESP-NOW
- `registerRoute()` → delega al `EspNowStrategy` (las rutas son solo para mesh)

```cpp
bool GatewayStrategy::send(uint8_t target, const uint8_t* data, size_t len) {
    if (target == 0) return _uart->send(target, data, len);
    return _espnow->send(target, data, len);
}
```

### Problema 4.2: Relay transparente de tramas (Gateway como router)

**Problema:** Si un nodo envía un comando destinado a otro nodo (no al Gateway), el Gateway debe reenviarlo sin procesarlo — actuar como router.

**Concepto:** Store-and-forward relay — si el DST_ID no es el mío ni broadcast, reenvío la trama sin alterar.

**Implementación:**
- `ProtocolEngine.cpp` — `parseFrame()`:
  ```cpp
  if (header.dst != _myId && header.dst != 0xFF) {
      // Not for me — relay it
      _strategy->send(header.dst, rawFrame, frameLen);
      return;
  }
  ```
- Excepción: SET_GPIO y otros comandos NO se reenvían automáticamente (previene loops)
- El Gateway (ID=1) tiene lógica especial: acepta tramas DST=1 para procesarlas localmente Y relay tramas DST≠1

---

## 5. Control Seguro de Hardware (GPIO)

### Problema 5.1: Evitar que un comando remoto destruya el dispositivo

**Problema:** Si un comando `SET_GPIO` puede escribir en cualquier pin, podría modificar pins de UART (crash de comunicación), SPI del flash (corrupción), o I2C (conflictos de bus). Esto es potencialmente destructivo.

**Concepto:** Pin Protection / Board Support Package (BSP) — lista blanca de pines seguros + lista negra de pines protegidos.

**Implementación:**
- `PinConfig.h` — `PROTECTED_PINS[]` = {1, 3 (UART0), 8-11 (SPI Flash), 16, 17 (UART2)}
- `isPinProtected(pin)` — consulta estática contra la lista
- `GpioController.cpp` — `execute(pin, value)`:
  1. Comprueba si `pin` está en `_managedPins` (whitelist) — si no, ignora silenciosamente
  2. Comprueba `isPinProtected(pin)` — si sí, ignora silenciosamente
  3. Solo entonces ejecuta `digitalWrite(pin, value)`
- **Política de rechazo silencioso** — no lanza excepciones ni errores (en embedded, un crash es peor que un no-op)

```cpp
void GpioController::execute(uint8_t pin, bool value) {
    if (!isPinManaged(pin)) return;     // Not in whitelist
    if (isPinProtected(pin)) return;    // In blacklist
    digitalWrite(pin, value ? HIGH : LOW);
}
```

### Problema 5.2: Declarar qué pines gestiona cada nodo

**Problema:** Cada nodo tiene un subconjunto diferente de pines válidos (el actuador usa 4-7 para relés, el sensor no controla ninguno). Se necesita configuración por nodo.

**Concepto:** Whitelist configurable por instancia.

**Implementación:**
- `SystemContext.h` — `setManagedPins(vector<uint8_t>)` almacena la lista de pines válidos
- `main_gateway.cpp` — `gateway.begin()` configura pins `{4, 5, 6, 7}` como managed
- `main_node_actuador.cpp` — configura los mismos pins para el actuador
- `GpioController` consulta `_managedPins` antes de ejecutar

---

## 6. Abstracción de Sensores

### Problema 6.1: Soportar múltiples tipos de sensores con una interfaz uniforme

**Problema:** DHT22 (I2C/single-wire), DS18B20 (OneWire), sensores de suelo capacitivos (ADC) — todos tienen APIs diferentes. Si el código de reporting los conoce directamente, cada nuevo sensor requiere cambios en la lógica de negocio.

**Concepto:** Polimorfismo via interfaz — todos los sensores implementan la misma interfaz `ISensor`, y el gestor los trata uniformemente.

**Implementación:**
- `ISensor.h` — Interfaz abstracta:
  ```cpp
  class ISensor {
      virtual bool init() = 0;
      virtual bool read(SensorReading& out) = 0;
      virtual const char* getName() = 0;
  };
  struct SensorReading { float value1; float value2; bool isValid; };
  ```
- `DHTSensor.cpp` — value1=temperatura, value2=humedad. Detecta NaN (fallo de lectura) → `isValid=false`
- `DS18B20Sensor.cpp` — value1=temperatura, value2=0. Bloquea ~750ms en `requestTemperatures()`
- `SoilMoistureSensor.cpp` — value1=porcentaje mapeado, value2=valor ADC raw. Calibración configurable (dry/wet thresholds)
- `SensorManager.cpp` — `readAll()` itera `vector<ISensor*>`, filtra lecturas inválidas, retorna solo las válidas

### Problema 6.2: Datos de simulación para desarrollo sin hardware

**Problema:** Desarrollar y testear el flujo completo (firmware → Raspberry → Backend → Frontend) requiere datos de sensores, pero no siempre hay hardware conectado.

**Concepto:** Mock mode — flag de compilación que activa generación de datos sintéticos realistas.

**Implementación:**
- `MOCK_DATA_ENABLED` — flag en `SystemManager.cpp`
- `DHTSensor.cpp` en mock mode — genera sinusoidal: `temp = 25 + 2*sin(millis())`, `hum = 50 + 5*cos(millis())`
- `DS18B20Sensor.cpp` en mock mode — `temp = 20 ± random(2°C)`
- `SoilMoistureSensor.cpp` en mock mode — `moisture = random(0-100%)`
- Los datos son plausibles (rango real) para testing de UI/gráficas

---

## 7. Ejecución No Bloqueante

### Problema 7.1: No usar `delay()` — nunca

**Problema:** En un microcontrolador, `delay()` bloquea el CPU completamente. Si un nodo está esperando 5 segundos entre reportes y llega un comando SET_GPIO, no lo procesa hasta que termine el delay. Esto es inaceptable en un sistema de control.

**Concepto:** Cooperative multitasking — usar `millis()` para comprobar el paso del tiempo sin bloquear.

**Implementación:**
- `SystemManager.cpp` — `update()` es el loop principal, llamado en cada iteración de `loop()`:
  ```cpp
  void SystemManager::update() {
      _engine.update();           // Procesa tramas pendientes
      runHandshakeLogic();        // Non-blocking handshake
      checkReportingInterval();   // Non-blocking sensor polling
      updateSequencer();          // Non-blocking sequence execution
  }
  ```
- `checkReportingInterval()`:
  ```cpp
  if (millis() - _lastReportTime >= _reportIntervalMs) {
      collectAndPublishSensorData();
      _lastReportTime = millis();
  }
  ```
- `runHandshakeLogic()` — comprueba timeout con `millis()`, no bloquea esperando SYN_ACK
- Toda la lógica es **polling cooperativo** — cada función retorna inmediatamente y se vuelve a llamar en el siguiente loop

### Problema 7.2: Máquina de estados en vez de flujo bloqueante

**Problema:** El handshake tiene 3 pasos que dependen de respuestas asíncronas. Un enfoque bloqueante (`send SYN, wait for SYN_ACK with timeout, send ACK`) bloquea todo lo demás durante hasta 6 segundos (3 intentos × 2s).

**Concepto:** State Machine — cada estado define qué hacer y a qué estado transicionar. El polling del `update()` evalúa el estado actual sin bloquear.

**Implementación:**
- `SystemContext.h` — `SystemState` enum: BOOT, HANDSHAKE_SEND_SYN, HANDSHAKE_WAIT_SYN_ACK, HANDSHAKE_SEND_ACK, IDLE, RUNNING, ERROR
- `SystemManager.cpp` — `runHandshakeLogic()`:
  ```cpp
  switch (_context.getState()) {
      case HANDSHAKE_SEND_SYN:
          sendSyn(targetId);
          setState(HANDSHAKE_WAIT_SYN_ACK);
          _handshakeStart = millis();
          break;
      case HANDSHAKE_WAIT_SYN_ACK:
          if (millis() - _handshakeStart > 2000) {
              if (++_handshakeAttempts >= 3) setState(ERROR);
              else setState(HANDSHAKE_SEND_SYN); // Retry
          }
          // SYN_ACK callback transitions to HANDSHAKE_SEND_ACK
          break;
      case HANDSHAKE_SEND_ACK:
          sendAck(targetId);
          setState(RUNNING);
          break;
  }
  ```
- Entre checks, el CPU es libre para procesar tramas UART/ESP-NOW

---

## 8. Especialización de Nodos

### Problema 8.1: Tres roles diferentes (Gateway, Sensor, Actuador) con código común

**Problema:** Los tres nodos comparten ProtocolEngine, SystemManager y la lógica de comunicación. Pero cada uno tiene comportamiento específico: el Sensor reporta telemetría, el Actuador ejecuta GPIO, el Gateway rutea entre interfaces. No se debe duplicar código.

**Concepto:** Template Method / Composición — clase base común con especialización por composición de componentes.

**Implementación:**
- `Node_Sensor.cpp` — Compone: SystemManager + SensorManager. En RUNNING, reporta periódicamente via `collectAndPublishSensorData()`
- `Node_Actuator.cpp` — Compone: SystemManager + GpioController. Pasivo: solo reacciona a callbacks SET_GPIO. Envía PIN_REPORT de vuelta.
- `Node_Gateway.cpp` — Compone: SystemManager + GpioController + SensorManager (híbrido). Gestiona relay entre UART↔ESP-NOW via GatewayStrategy.

| Nodo | SensorManager | GpioController | Handshake | Reporting |
|------|:---:|:---:|:---:|:---:|
| Sensor | ✓ | ✗ | Inicia SYN | Periódico |
| Actuador | ✗ | ✓ | No (RUNNING directo) | Reactivo (PIN_REPORT) |
| Gateway | ✓ | ✓ | Acepta SYN | Relay + local |

### Problema 8.2: Cada nodo tiene su propio main entry point

**Problema:** Tres firmwares diferentes deben compilar del mismo repo sin interferencias.

**Concepto:** Build Source Filtering — PlatformIO compila solo los archivos relevantes para cada entorno.

**Implementación en `platformio.ini`:**
```ini
[env:gateway]
build_src_filter = +<main_gateway.cpp> +<core/> +<communications/> +<hardware/>

[env:sensor]
build_src_filter = +<main_node_sensor.cpp> +<core/> +<communications/> +<hardware/>

[env:actuador]
build_src_filter = +<main_node_actuador.cpp> +<core/> +<communications/> +<hardware/>
```
- Cada `main_*.cpp` crea sus propias instancias de Strategy, ProtocolEngine y Node
- El linker solo incluye el código realmente referenciado

---

## 9. Orquestación de Secuencias

### Problema 9.1: Ejecutar macros de riego (encender bomba 5s, abrir válvula 10s, cerrar, apagar) sin bloquear

**Problema:** Una secuencia de riego puede tener 10 pasos con delays de segundos entre cada uno. Si se ejecuta con `delay()`, el nodo queda sordo a nuevos comandos durante toda la secuencia.

**Concepto:** Non-blocking Sequencer — máquina de estados que avanza un paso cuando el timer del paso anterior expira, sin `delay()`.

**Implementación:**
- `SystemManager.cpp` — `updateSequencer()`:
  ```cpp
  if (_sequenceActive && millis() - _stepStart >= currentStep.delayMs) {
      executeStep(_steps[_currentStepIndex]);  // digitalWrite
      _currentStepIndex++;
      _stepStart = millis();
      if (_currentStepIndex >= _steps.size()) _sequenceActive = false;
  }
  ```
- `InternalTypes.h` — `SequenceStep { uint8_t pin; bool value; uint32_t delayMs; }`
- `EXEC_SEQUENCE (0x30)` callback → parsea la lista de pasos → activa el secuenciador
- Entre pasos, `update()` sigue procesando tramas normalmente — el nodo es completamente responsivo

---

## 10. Testabilidad sin Hardware

### Problema 10.1: Unit tests de protocolo y lógica sin placa ESP32

**Problema:** Compilar y flashear al ESP32 para cada test tarda minutos. Se necesita poder ejecutar tests en el PC de desarrollo (Linux/Mac/Windows).

**Concepto:** Native test environment — compilar con g++ (no xtensa-gcc), reemplazando dependencias de hardware con mocks.

**Implementación:**
- `platformio.ini` — entorno `[env:native]` con `platform = native` y `build_flags = -DNATIVE_ENV`
- `test/mocks/Arduino.h` — Stubs para `millis()`, `delay()`, `Serial`, `pinMode()`, `digitalWrite()`, `map()`
- `test/mocks/MockComms.h` — Implementa `IComms`: `send()` captura TX en buffer, `pushRxData()` simula recepción, tracks route registrations
- `test/mocks/MockSensor.h` — Retorna temperatura/humedad configurable
- `#ifdef NATIVE_ENV` en EspNowStrategy — simula broadcast entre instancias estáticas en vez de WiFi real

### Problema 10.2: Verificar el protocolo end-to-end en tests

**Problema:** Se necesita validar que un frame empaquetado se puede desempaquetar correctamente, que el CRC funciona, que los callbacks se disparan.

**Concepto:** Round-trip testing — empaquetar un comando, inyectarlo como RX en el mock, y verificar que se parsea y despacha correctamente.

**Implementación:**
- `test_protocol_engine.cpp`:
  ```cpp
  // 1. Crear motor con MockComms
  MockComms mock;
  ProtocolEngine engine(&mock, 1);

  // 2. Registrar callback
  bool called = false;
  engine.onSetGpio([&](const SetGpioCmd& cmd) { called = true; });

  // 3. Construir frame manualmente con CRC válido
  uint8_t frame[] = {0xFE, 3, 0, 2, 1, 0x10, 4, 1, 0, CRC};
  mock.pushRxData(frame, sizeof(frame));

  // 4. Procesar y verificar
  engine.update();
  TEST_ASSERT_TRUE(called);
  ```
- `test_system_manager.cpp` — Verifica transiciones de estado del handshake
- `test_gpio_controller.cpp` — Verifica protección de pines

---

## 11. Compilación Selectiva

### Problema 11.1: Un solo repo para 6+ variantes de firmware

**Problema:** Gateway, sensor, actuador, sensor_cluster, sensor_deepsleep, sensor_test — todas son variantes diferentes que comparten la mayoría del código pero difieren en el `main` y en las dependencias de hardware.

**Concepto:** Build Source Filtering de PlatformIO — cada entorno declara qué archivos incluir.

**Implementación en `platformio.ini`:**
```ini
[env:gateway]
board = esp32-s3-devkitc-1
build_src_filter = +<main_gateway.cpp> +<core/> +<communications/> +<hardware/>
build_flags = -DNODE_ID=1

[env:sensor]
board = esp32-s3-devkitc-1
build_src_filter = +<main_node_sensor.cpp> +<core/> +<communications/> +<hardware/>
build_flags = -DNODE_ID=2

[env:sensor_cluster]
build_src_filter = +<main_sensor_cluster.cpp> +<core/> +<communications/> +<hardware/>
build_flags = -DNODE_ID=2

[env:native]
platform = native
build_flags = -DNATIVE_ENV
test_filter = test_unitarios/*
```

- `build_src_filter` — el `+<>` incluye, el `-<>` excluye. Solo `main_gateway.cpp` OR `main_node_sensor.cpp` se compila, nunca ambos.
- `build_flags` — `-DNODE_ID=X` inyecta el ID en compile time (no configurable en runtime)
- `lib_deps` — cada entorno lista solo las librerías que necesita (DHT solo para sensor, FastLED solo para actuador)

---

## 12. Resiliencia en ISR y Buffers

### Problema 12.1: Recibir datos ESP-NOW en contexto de interrupción sin corrupción

**Problema:** `onDataRecv()` de ESP-NOW se ejecuta en contexto ISR (interrupt). No se puede hacer malloc, usar String, ni llamar a funciones de Arduino complejas. Si se procesa el frame aquí, se puede corromper la pila.

**Concepto:** Zero-allocation ISR buffer — copiar los bytes a un buffer estático en el ISR y procesarlos fuera, en el loop principal.

**Implementación:**
- `EspNowStrategy.cpp`:
  ```cpp
  // Callback ISR — solo copia bytes, nada más
  static uint8_t _rxBuffer[256];
  static size_t _rxLen = 0;

  static void onDataRecv(const uint8_t* mac, const uint8_t* data, int len) {
      if (len > sizeof(_rxBuffer)) return;  // Drop oversized
      memcpy(_rxBuffer, data, len);
      _rxLen = len;
      // Auto-learn peer MAC from source
  }
  ```
- `read()` (llamado desde el loop principal) — copia `_rxBuffer` a un vector y resetea `_rxLen = 0`
- El procesamiento real (parseFrame, callbacks) ocurre fuera del ISR

### Problema 12.2: Sincronización de canal WiFi en ESP32-S3

**Problema:** ESP32-S3 tiene un bug conocido donde el canal WiFi se desincroniza después de un tiempo, causando que ESP-NOW deje de recibir.

**Concepto:** Channel pinning — forzar el canal WiFi al iniciar y activar modo promiscuo para mantener la sincronización.

**Implementación:**
- `EspNowStrategy.cpp` — en `begin()`:
  ```cpp
  esp_wifi_set_promiscuous(true);   // Fuerza listening en canal
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);
  ```
- Canal 1 hardcodeado — todos los nodos deben usar el mismo canal

---

## Resumen Visual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     FIRMWARE — PROBLEMAS RESUELTOS                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  COMUNICACIÓN              PROTOCOLO BINARIO       HANDSHAKE            │
│  ├ Strategy (IComms)       ├ Framing + CRC         ├ 3-way SYN/ACK     │
│  ├ UART + ESP-NOW          ├ Fixed-point floats    ├ State machine      │
│  └ Routing dinámico        ├ CMD dispatch          └ Timeout + retries  │
│                            └ 6 bytes header                             │
│                                                                         │
│  ENRUTAMIENTO              GPIO SEGURO             SENSORES             │
│  ├ Composite Gateway       ├ Protected pins        ├ ISensor interface  │
│  └ Relay transparente      ├ Managed whitelist     ├ DHT/DS18B20/Soil  │
│                            └ Rechazo silencioso    └ Mock mode          │
│                                                                         │
│  NO BLOQUEANTE             ESPECIALIZACIÓN         SECUENCIAS           │
│  ├ millis() polling        ├ Sensor/Actuator/GW    └ Non-blocking       │
│  └ State machine           ├ Composición               sequencer        │
│                            └ build_src_filter                           │
│                                                                         │
│  TESTABILIDAD              COMPILACIÓN             RESILIENCIA ISR      │
│  ├ Native tests (g++)      ├ 6+ build envs         ├ Static RX buffer  │
│  ├ MockComms/MockSensor    └ Source filtering       └ Channel sync fix  │
│  └ Round-trip CRC test                                                  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
