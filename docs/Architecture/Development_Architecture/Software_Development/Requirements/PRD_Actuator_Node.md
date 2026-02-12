# PRD: Actuator Node (Window Control)

## 1. Overview
A specialized ESP32 node designed to control a DC motor for greenhouse windows via a contactor/relay. It reports its state and battery level back to the gateway.

## 2. Hardware Specifications
- **MCU**: ESP32 (WROOM or S3).
- **Actuator**: Relays/Contactors controlling a DC Motor.
- **Sensors**: 
    - **Limit Switches (Final de Carrera)**: Detect fully open/closed states.
    - **Battery Voltage**: Voltage divider on ADC pin.
- **Communication**: ESP-Now (Protocol V2).
- **Power**: Battery powered with Solar charging (requires Light Sleep).

## 3. Product Features

### A. Motor Control
- **Command**: Accepts `SET_GPIO` (CmdId 0x10).
- **Action**: Toggles GPIO to activate/deactivate the contactor.
- **Limit Safety**: Logic to stop motor if limit switch is triggered (Future/Firmware Logic).

### B. Telemetry & Feedback
- **Immediate Reporting**: Upon state change, sends a Report.
- **Data Content**:
    - `Value1`: Motor State (1.0 = ON, 0.0 = OFF).
    - `Value2`: Battery Voltage (e.g., 12.5V).
- **Ping/Pong**: Responds to PING for availability checks.

### C. Power Management
- **Light Sleep**: Enters Light Sleep when idle to save power.
- **Wake Up**: Wakes up on ESP-Now reception (Magic Packet/broadcast) or Timer.

## 4. Architecture & Protocol

### Firmware (`main_node_actuador_ventana.cpp`)
- **Base**: `ProtocolEngine` + `EspNowStrategy`.
- **Logic**: 
    - Registers `onSetGpio` callback.
    - On callback: `digitalWrite`, `analogRead(BAT)`, `sendDataReport`.
- **Addressing**: Hardcoded MAC for prototype (Target: Gateway).

### Python Backend & Mock
- **Mock Mode**: Supports `--mock-actuator`.
- **Simulation Flow**:
    1.  GUI sends `SET_GPIO`.
    2.  Mock receives frame.
    3.  Mock waits (simulating latency).
    4.  Mock replies with `DATA_REPORT` (GPIO State + Simulated Battery).
    5.  Mock simulates "Sleep".

### GUI
- New Section: **"Control Ventanas"**.
- Button: "ABRIR / CERRAR" (Toggle).
- Visual Indicator: Motor State & Battery Level.

## 5. Implementation Plan

### Phase 1: Firmware
1.  Create `C++/src/main_node_actuador_ventana.cpp`.
2.  Implement `handleSetGpio` function.
3.  Implement Battery Reading function.

### Phase 2: Python Mock
1.  Update `MockTransport` to inspect outgoing TX packets (detect `SET_GPIO`).
2.  Generate reactive RX packets (`DATA_REPORT`).

### Phase 3: GUI
1.  Add specific controls to `DemeterGuiApp`.
2.  Bind commands to buttons.

## 6. Verification
- **Test 1 (Mock)**: Click button -> Log shows "TX SET_GPIO" -> Log shows "RX DATA_REPORT (Motor=1, Bat=12.5)".
- **Test 2 (Hardware)**: Connect ESP32 with LED (representing Relay). Send command -> LED toggles -> Python receives report.
