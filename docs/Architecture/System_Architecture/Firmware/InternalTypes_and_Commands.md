# InternalTypes and Command Flow (Demeter V2)

This document details the internal data structures used to decouple the Wire Protocol (ProtocolEngine) from the Application Logic (SystemManager), and explains the flow of commands.

## 1. Philosophy: Struct-Based Decoupling

The firmware uses a **Struct-Based** approach to handle commands. 
- **ProtocolEngine** parses raw bytes and populates a specific `Demeter::Struct`.
- **SystemManager** receives this `Struct` via a callback.
- **ProtocolEngine** sends commands taking this `Struct` as an argument.

This ensures that adding fields to a command (e.g., a "Force" flag to GPIO) only requires updating the `Struct` definition and the serializer/deserializer, without breaking every function signature in the chain.

## 2. Internal Types (`Demeter` Namespace)

Defined in `include/core/InternalTypes.h`.

### Control Commands

| Command | Struct | Fields | Description |
| :--- | :--- | :--- | :--- |
| **SET_GPIO** | `SetGpioCmd` | `pin` (u8), `value` (bool), `flags` (u8) | Controls a Digital Output. Flags can be used for overrides or timing. |
| **SET_PWM** | `SetPwmCmd` | `pin` (u8), `value` (u16) | Controls an Analog/PWM Output. Value is 0-65535 (or scaled). |
| **EXEC_SEQUENCE** | `ExecSequenceCmd` | `steps` (vector<SequenceStep>) | Executes a list of timed GPIO actions. |
| **ROUTE_ADD** | `RouteAddCmd` | `nodeId` (u8), `mac` (array<u8,6>) | Registers a static route in the mesh/network layer. |

### Telemetry & Reports

| Command | Struct | Fields | Description |
| :--- | :--- | :--- | :--- |
| **TEMP_HUM_REPORT** | `TempHumReport` | `sourceId` (u8), `temperature` (float), `humidity` (float) | Environmental data. |
| **PIN_REPORT** | `PinReport` | `sourceId` (u8), `pin` (u8), `state` (bool) | Feedback on actual pin state. |
| **SYSTEM_REPORT** | `SystemReport` | `sourceId` (u8), `mode` (u8), `batteryMv` (u16) | Device health and status. |

### Handshake & Network

| Command | Struct | Fields | Description |
| :--- | :--- | :--- | :--- |
| **PING** | `RequestData` | `sourceId` (u8) | Alive check. Application layer must ACK. |
| **GET_SENSORS** | `RequestData` | `sourceId` (u8) | Request for immediate sensor read. |
| **SYN** | `AckData` | `sourceId` (u8), `context` (u8/enum) | Handshake Start. Context usually 0. |
| **SYN_ACK** | `AckData` | `sourceId` (u8), `context` (u8/enum) | Handshake Response. |
| **ACK** | `AckData` | `sourceId` (u8), `context` (u8) | Generic Confirmation. Context depends on what is being ACKed. |
| **NACK** | `NackData` | `sourceId` (u8), `errorCode` (u8) | Generic Rejection/Error. |

## 3. Command Flow

### General Principle: "Pure IO"
The `ProtocolEngine` is a **Pure IO** component. It does **not** make decisions.
- It **never** sends an ACK automatically (except low-level transport ACKs which are invisible here).
- It **never** executes a GPIO action directly.
- It simply converts `Bytes <-> Structs`.

### Receive Flow (RX)
1. **Network**: Bytes arrive via `IComms` (UART/ESP-Now).
2. **ProtocolEngine**: 
   - Validates CRC/Header.
   - Identifies Command ID.
   - Deserializes payload into specific Struct (e.g., `SetGpioCmd`).
   - Calls the registered Callback (e.g., `_onGpioCommand(cmd)`).
3. **SystemManager**:
   - Callback receives `cmd`.
   - Decides logic (e.g., "Am I allowed to switch this pin?").
   - **Executes** action (via `GpioController`).
   - **Sends Feedback** if required (e.g., `sendAck` or `sendPinReport`).

### Transmit Flow (TX)
1. **SystemManager**: 
   - Decides to send data.
   - Populates a Struct (e.g., `RouteAddCmd`).
   - Calls `_engine->sendRouteAdd(target, cmd)`.
2. **ProtocolEngine**:
   - Serializes Struct into Bytes.
   - Wraps in Header/CRC.
   - Sends via `IComms`.

## 4. Specific Scenarios

### Route Addition (Configuration)
1. **Gateway** sends `ROUTE_ADD` (Struct: `RouteAddCmd`).
2. **Node ProtocolEngine** parses -> `onRouteAddRecv(cmd)`.
3. **Node SystemManager**:
   - Helper function `handleRouteAdd(cmd)`.
   - Calls `_engine->registerRoute(cmd.nodeId, cmd.mac)`.
   - Sends `ACK` back to Gateway manually: `_engine->sendAck(...)`.

### Handshake
1. **Node A** sends `SYN` (`AckData` with context 0).
2. **Node B ProtocolEngine** -> `onSynRecv`.
3. **Node B SystemManager**:
   - Logic: "Do I accept connection?"
   - Yes: Sends `SYN_ACK` (`AckData`).
4. **Node A ProtocolEngine** -> `onSynAckRecv`.
5. **Node A SystemManager** -> Sends Final `ACK`.

This architecture ensures the `ProtocolEngine` remains reusable and testable (Mock IO), while `SystemManager` owns the "Personality" of the device.
