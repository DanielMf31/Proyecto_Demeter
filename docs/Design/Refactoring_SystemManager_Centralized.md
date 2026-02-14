# Centralized SystemManager & Contextual Handshake Design

## Overview
The goal is to strictly encapsulate all protocol communication within `SystemManager`. Nodes (`Node_Sensor`, `Node_Actuator`, `Node_Gateway`) must NOT interact with `ProtocolEngine` directly. Additionally, the Handshake process will be enhanced to include context (e.g., "Session Type") in the final `ACK` to prepare the receiver for specific data processing.

## 1. SystemManager as Communication Facade
`SystemManager` will become the sole gateway for sending and receiving application-level messages. `ProtocolEngine` remains the low-level framing mechanism, but it is now a private implementation detail of `SystemManager` (or at least, only accessed by it).

### New Capabilities
`SystemManager` will expose high-level methods for Nodes:
*   `sendSensorData(float temp, float hum)`
*   `sendPinStatus(uint8_t pin, bool state)`
*   `sendSystemStatus(uint8_t mode, uint16_t batt)`
*   `requestSensors(uint8_t targetId)`

It will also implement all protocol callbacks internally:
*   `_engine->onTempHumReportRecv(...)` -> `SystemManager::handleTempHumReport(...)`
*   `_engine->onPinReportRecv(...)` -> `SystemManager::handlePinReport(...)`
*   etc.

## 2. Contextual ACK (Enhanced Handshake)
To improve state synchronization, the 3-Way Handshake will carry "Intent" or "Context" in the final `ACK`.

**Flow:**
1.  **SYN** (No Payload): "Hello?"
2.  **SYN-ACK** (No Payload): "I am here."
3.  **ACK** (With Context): "Great. I am entering session mode: SENSOR_REPORT."

Upon receiving the Contextual ACK, the Receiver can transition to a specific state (e.g., `RECEIVING_SENSOR_DATA`) or simply log the expected content.

### Implementation Details

#### InternalTypes.h
Define `SessionType` or `ContextFlags`:
```cpp
enum class SessionContext : uint8_t {
    GENERAL = 0x00,
    SENSOR_DATA = 0x01,
    COMMAND_MODE = 0x02,
    FW_UPDATE = 0xFF
};
```

#### ProtocolEngine
Update `sendAck` to accept an optional payload byte (context).
```cpp
void sendAck(uint8_t targetId, uint8_t context = 0);
```

#### SystemManager
*   `initiateHandshake(uint8_t targetId, SessionContext context)`
*   Store `_targetSessionContext`.
*   In `handleSynAckRecv`, send `ACK` with `_targetSessionContext`.
*   In `handleAckRecv`, read context and update state if necessary.

## 3. Node Refactoring Logic
Nodes will essentially become hardware wrappers and "User Interface" (Serial/Button) handlers.
Example `Node_Sensor::update()`:
```cpp
void collectAndSend() {
    // Read HW
    auto data = _sensorManager->readAll();
    // Send via SystemManager
    _systemManager->sendSensorData(1, data.temp, data.hum); 
}
```

## 4. Implementation Steps
1.  **Update `InternalTypes.h`**: Add `SessionContext`.
2.  **Update `ProtocolEngine`**: Modify `sendAck` to support context byte.
3.  **Update `SystemManager.h/cpp`**: 
    *   Add Session Context support.
    *   Add all `handleX` methods and `sendX` methods.
4.  **Refactor Nodes**: Switch all `_engine->sendX` calls to `_systemManager->sendX`.
