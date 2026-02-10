# Raspberry Pi 4 (Server)

**Role:** Central Server, Database, User Interface (HMI)
**OS:** Raspberry Pi OS (Linux ARM64)

## Specifications
- **Model:** Raspberry Pi 4 Model B
- **Connectivity:**
    - **UART (GPIO 14/15):** Physical connection to Gateway.
    - **WiFi/Ethernet:** Local network access and SSH.
    - **HDMI:** Video output for GUI.

## Software Stack
### Demeter Backend (async_service.py)
- Asynchronous Python service using `asyncio`.
- Manages Protocol V2 communication via UART.
- Stores data in SQLite (`demeter_data.db`).
- TCP Server (Port 8888) for GUI connection.
- **Mock Mode:** Simulates data without hardware using `--mock` flag.
- **Configuration:** Centralized in `.env` and `config/`.

### Demeter GUI (main_gui.py)
- Professional interface built with `CustomTkinter`.
- Optimized for touch screens.
- Visualizes sensor data, controls actuators, and manages users.

### Grafana
- Visualization server for historical data (Port 3000).
- Reads directly from the SQLite database.

## Control Capabilities
- **Terminal (SSH/Local):** Full system control, deployment, logs, database access.
- **GUI (Touch/Mouse):** Daily operation interface.
- **Web (Grafana):** Remote data analysis.
