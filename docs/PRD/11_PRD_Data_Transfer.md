# PRD: Data Transfer & Telemetry

## 1. Introduction
The objective is to enable real-time telemetry (Temperature and Humidity) transmission from the Remote Node to the Gateway, and subsequently to the Python Interface for visualization and logging.

## 2. Requirements

### 2.1 Firmware (Node)
*   **Packet Structure**: Define a new Command ID `CMD_DATA_REPORT` (0x0B).
*   **Payload**: 4 Bytes.
    *   Temp (2 bytes): Int16 (scaled x100) or Float. Let's use **Int16** for simplicity (e.g., 25.43 -> 2543).
    *   Hum (2 bytes): Int16 (scaled x100).
*   **Trigger**:
    *   Automatic interval (e.g., every 5 seconds).
    *   On-Demand (Response to a specific GET_DATA command - Optional for now).

### 2.2 Firmware (Gateway)
*   **Forwarding**: The Gateway must forward received `CMD_DATA_REPORT` packets from ESP-Now to UART (Host).
*   **Transparent Bridge**: `ProtocolEngine`'s existing routing logic (Dst=0) should handle this, but we need to ensure the Node addresses the Host (ID 0).

### 2.3 Python Backend
*   **Protocol Parser**: Update `ProtocolParser` to handle `CMD_DATA_REPORT` (0x0B).
*   **Data Model**: Extract Temp/Hum from payload and convert back to Float.
*   **Event Dispatch**: Emit an event `data_received` with the values.

### 2.4 User Interface
*   **New Window**: `DataVisualizationWindow`.
*   **Components**:
    *   Big Labels for Temperature and Humidity.
    *   (Optional) Simple progress bar or gauge.
    *   "Real-time" indicator.
*   **Integration**: Add button in Main Window to open this view.

### 2.5 Logging
*   **Sensor Logger**: A dedicated CSV or Log file (`logs/sensor_data.log`) that records:
    *   Timestamp
    *   Node ID
    *   Temperature
    *   Humidity

## 3. Implementation Details

### 3.1 Protocol Definition (V2 Extension)
*   **Command**: `DATA_REPORT = 0x0B`
*   **Format**: `[HEAD] [LEN] [FLAGS] [SRC] [DST] [CMD] [PAYLOAD...] [CRC]`
    *   `SRC`: Node ID (e.g., 2)
    *   `DST`: Host ID (0)
    *   `PAYLOAD`: `[T_LSB] [T_MSB] [H_LSB] [H_MSB]`

### 3.2 Design Decisions
*   **Scaling**: Using Int16 x100 avoids float issues across platforms.
*   **Architecture**:
    *   Use **Observer Pattern** in Python: `DeviceManager` or `ProtocolEngine` publishes, UI subscribes.

## 4. Success Criteria
1.  Node sends data every X seconds.
2.  Gateway forwards it.
3.  Python logs it to file.
4.  GUI updates in real-time.
