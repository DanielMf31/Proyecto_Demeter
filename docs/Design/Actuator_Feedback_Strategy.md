# Actuator Feedback Strategy: Design & Implementation Plan

## Problem
Currently, the system uses a **hack** to report Actuator State (Window Open/Closed) by overloading the `DataReport` message:
- `Temperature` -> Mapped to `Pin State` (0.0/1.0).
- `Humidity` -> Mapped to `Battery Level`.

This causes confusion ("Temp=0.0") and prevents sending actual environmental data from actuator nodes if they have sensors.

## Proposed Solution: Explicit `ActuatorReport` Message
We will extend the Demeter V2 Protocol to support a dedicated message type for actuator feedback.

### 1. Protocol Definition
**New Command ID**: `ACTUATOR_REPORT = 0x0C` (12)

**Binary Structure (Payload)**:
`[PIN(1)] [STATE(1)] [BATTERY_mV(2)]` = 4 Bytes
- **PIN**: Physical Pin Number (uint8).
- **STATE**: 0=OFF, 1=ON (uint8).
- **BATTERY**: Battery voltage in millivolts (uint16). Example: 12500 = 12.5V.

### 2. Schema Changes (`shared/schemas.py`)
Add a new Pydantic model:
```python
class ActuatorReport(DemeterCommand):
    node_id: int
    pin: int
    state: int
    battery_mv: int
    
    def get_cmd_id(self) -> int: return CmdId.ACTUATOR_REPORT
```

### 3. Implementation Plan

#### Phase 1: Core & Protocol
1.  **Modify `schemas.py`**: Add `ACTUATOR_REPORT` to `CmdId` enum and create `ActuatorReport` class.
2.  **Modify `protocol_v2.py`**: 
    - serialization: Handle `ActuatorReport` -> pack `b'<BBH'`.
    - deserialization: Handle `0x0C` -> unpack `b'<BBH'` -> return `ActuatorReport`.

#### Phase 2: Mock & Service
3.  **Modify `MockTransport` (`ActionStrategy`)**: 
    - Instead of sending `DataReport` with fake temp, send `ActuatorReport` with `state` and `battery_mv`.
4.  **Modify `DemeterService`**: 
    - Ensure it forwards this new message type to TCP clients (GUI) just like it does for `DataReport`.

#### Phase 3: GUI
5.  **Modify `gui_app.py`**:
    - Listen for `ActuatorReport` JSON messages.
    - Update "Estado" and "Batería" labels based on this specific message.
    - Decouple from `DataReport` logic (which should only show Temp/Hum).

## Benefits
- **Semantic Clarity**: No more "Temperature = 0.0" confusion.
- **Scalability**: Actuator nodes can now *also* have sensors and send `DataReport` separately if needed.
- **Precision**: Battery reported in mV allows better monitoring.
