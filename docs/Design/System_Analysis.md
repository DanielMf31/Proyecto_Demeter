# System Analysis: Demeter V2 Python Architecture

## 1. Server Architecture (`Python/src/proyecto_demeter/core`)

The backend service is the core of the Demeter system. It manages hardware communication, data persistence, and client connections.

### Entry Point: `main_async.py`
- **Role**: Launcher & Process Manager.
- **Key Responsibilities**:
    - Configuring Logging based on user settings.
    - Parsing CLI arguments (e.g., `--port`, `--mock`, `--mock-actuator`).
    - managing the environment variables for the service process.
    - Starting the `async_service.py` as a subprocess.
    - Handling shutdown signals (SIGINT/SIGTERM) gracefully.
    - **Port Cleanup**: Checks if port 8888 (TCP) is busy and kills the process occupying it before starting.

### Core Service: `async_service.py` (`DemeterService`)
- **Role**: The main application logic.
- **Key Components**:
    - **Transport**: Abstraction for UART communication. Switches between `AsyncUartTransport` (Hardware) and `MockTransport` (Simulation) based on configuration.
    - **Protocol**: Instance of `DemeterProtocolV2` for parsing/serializing binary frames.
    - **TCP Server**: Listens on port 8888 for connections from the GUI/TUI.
    - **Data Manager**: Async interface to SQLite (`data/database.py`).
    - **Sensor Logger**: CSV logging for redundancy (`data/file_logger.py`).
- **Data Flow**:
    1. **Rx (UART)**: `on_uart_data` -> `process_buffer` -> `protocol.parse_frame` -> `handle_protocol_command`.
    2. **Processing**: Sensor data is logged to DB/CSV and broadcasted to TCP clients.
    3. **Tx (TCP -> UART)**: Commands from GUI are validated via Pydantic (`GpioCommand`, etc.), processed (mock or real execution), and sent to transport.

---

## 2. Graphical Interface (`Python/src/proyecto_demeter/ui/gui_app.py`)

A modern desktop application built with `customtkinter` (CTk).

### Architecture
- **Hybrid Loop**: Runs the `tkinter` mainloop in the main thread and an `asyncio` loop in a separate daemon thread (`network_thread`). This ensures the UI remains responsive while handling network I/O.
- **Communication**: Connects as a TCP Client to `localhost:8888`.
- **Protocol**: Sends/Receives JSON messages (serialized Pydantic models).

### Key Features
- **GPIO Control**: Buttons to toggle specific pins (Target: Gateway/Actuator).
- **Actuator Window (Node 3)**:
    - Dedicated section for Window Control.
    - Visualizes State (Open/Closed) and Battery.
    - **Note on Visualization**: The `MockTransport` simulates the actuator state by mapping `1 (ON)` to `Temp=1.0` and `0 (OFF)` to `Temp=0.0`. The GUI reads this "temperature" to update the UI label (Open/Closed). This is a visual hack for the mock environment.
- **Live Logs**: Displays a real-time log of sent/received commands.

---

## 3. Mock System (`mock_transport.py`)

Redesigned with the **Strategy Pattern** to support varied testing scenarios.

### Modes
1.  **SENSORS**: Simulates Nodes 10 & 11 sending periodic environmental data.
2.  **ACTUATOR**: Simulates Node 3 (Window) responding to `PING` and `SET_GPIO`.
    - **Logic**: When `SET_GPIO` is received, it updates internal state and sends a `DataReport` confirming the new state (mapped to Temperature field).
3.  **MIXED**: Runs both concurrently.

### "Temp=0.0" Explanation
In **Actuator Mode**, the system replies with a `DataReport`. Since the standard `DataReport` schema requires `temperature` and `humidity`, the mock uses these fields to carry state information:
- **Temperature**: Represents GPIO State (`1.0` = ON/OPEN, `0.0` = OFF/CLOSED).
- **Humidity**: Represents Battery Level (starts at 12.6V and drains).

This alerts the GUI to update the "Estado" label without needing a dedicated "ActuatorReport" packet type in the current protocol version.
