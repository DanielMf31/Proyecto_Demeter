# Protocol V2 Tests Explanation

## Overview
This document details the testing strategy and rationale for the `DemeterProtocolV2` implementation. The tests are located in `tests/test_protocol_v2.py` and are designed to verify the robustness of the custom binary protocol used for communication between the Gateway, Sensors, and Actuators.

## Test Categories

### 1. Serialization Tests (Model -> Bytes)
**Goal:** Ensure that high-level Pydantic models are correctly converted into the binary format required by the hardware nodes.

*   **`test_serialize_ping`**: Verifies the simplest command structure. Checks header fields (Sync, Len, CmdId) and ensures payload length is 0.
*   **`test_serialize_ack` / `nack`**: Verifies that feedback commands correctly pack the `Original Command ID` and `Error Codes`. Critical for reliable communication flow.
*   **`test_serialize_syn` / `syn_ack`**: **(New)** Verifies the Handshake commands. Ensures the `context` byte is correctly placed in the payload. This is essential for the `IDLE` -> `ACTIVE` state transition.
*   **`test_serialize_set_gpio`**: Checks packing of control parameters (Pin, Value) and flags.
*   **`test_serialize_set_pwm`**: Verifies multi-byte value packing (uint16 little-endian) for PWM duty cycles.
*   **`test_serialize_route_add`**: Tests handling of raw bytes fields (MAC address) within the payload.
*   **`test_serialize_exec_sequence`**: Verifies complex, nested structures. Ensures the `SequenceStep` list is correctly serialized with a count prefix and consistent step size.
*   **`test_serialize_system_report`**: **(New)** Verifies packing of the System Report, including Mode (uint8), Battery Voltage (uint16), and Reserved bytes.

### 2. Deserialization Tests (Bytes -> Model)
**Goal:** Verify that binary frames received from hardware are correctly parsed back into Python objects.

*   **`test_parse_valid_ping` / `set_gpio`**: Basic round-trip verification.
*   **`test_parse_handshake`**: **(New)** confirms `Syn` and `SynAck` frames are recognized and mapped to their respective classes.
*   **`test_parse_reports`**:
    *   `TempHumReport`: Verifies floating-point data reconstruction.
    *   `PinReport`: Verifies feedback parsing.
    *   `SystemReport`: **(New)** Checks extraction of system health data (Mock/Battery).

### 3. Edge Cases & Validation
**Goal:** Ensure the protocol handler does not crash on bad data and enforces constraints.

*   **`test_crc_failure`**: Modifies the last byte of a valid frame to ensure the parser returns `None` (rejects corruption).
*   **`test_incomplete_frame`**: Feeds truncated data to ensuring safety against fragmented packets.
*   **`test_garbage_data`**: Feeds random noise to verify the parser resets/ignores it.
*   **`test_unknown_cmd_id`**: Ensures forward compatibility or safe failure when receiving undefined commands.
*   **`test_demeter_command_base`**: **(New)** Verifies that the Pydantic models enforce valid ranges (e.g., `target_id` <= 254) and that the base class cannot be instantiated directly.

## Rationale for Recent Additions
*   **Syn/SynAck**: Added to support the new "Connection Handshake" logic required for the `IDLE`/`ACTIVE` mode switching.
*   **SystemReport**: Essential for the Dashboard to display node status (Battery, Sleep Mode) beyond just sensor data.
*   **Base Class Test**: Ensures strict type safety and validation rules across all commands.
