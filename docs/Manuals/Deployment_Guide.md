# 🚀 Demeter Version 2.0 - Deployment Guide

This guide details the steps to deploy the full Demeter system:
1.  **Hardware**: ESP32 Node (Transmitter) & ESP32 Gateway (Receiver).
2.  **Firmware**: Flashing the C++ code.
3.  **Software**: Running the Python Backend & GUI on the Raspberry Pi.

---

## 1. Hardware Setup

1.  **Gateway (Coordinator)**:
    *   Connect an **ESP32-S3** to the Raspberry Pi (or your PC) via USB.
    *   **Note the Port**: Typically `/dev/ttyACM0` or `/dev/ttyUSB0`.

2.  **Node (Sensor)**:
    *   Connect another **ESP32-S3** to a power source (USB or Battery).
    *   Ensure sensors (DHT, DS18B20, Soil) are connected to the pins defined in `C++/src/main_node.cpp`.

---

## 2. Firmware Flashing (PlatformIO)

Open a terminal in the project root (`Proyecto_Demeter`).

### A. Flash the Gateway
Connect the **Gateway ESP32**.

```bash
# Upload Gateway Firmware
pio run -t upload -e gateway --upload-port /dev/ttyACM0
```
*(Replace `/dev/ttyACM0` with your actual port if different)*

### B. Flash the Node
Connect the **Node ESP32**.

```bash
# Upload Node Firmware
pio run -t upload -e transmisor --upload-port /dev/ttyACM1
```

> **Tip**: You can monitor the serial output to verify it's working:
> `pio device monitor -p /dev/ttyACM0 -b 115200`

---

## 3. Python Server Setup (Raspberry Pi)

The Python service runs on the Raspberry Pi, communicates with the Gateway via UART, and saves data to SQLite.

### A. Prepare Environment

```bash
cd ~/Documentos/PlatformIO/Projects/Proyecto_Demeter
source Python/.venv/bin/activate
pip install -r Python/requirements.txt  # Ensure deps are installed
```

### B. Start the Backend Service
Run this in a **dedicated terminal**. It acts as the system server.

```bash
# Starts the Service (UART + TCP Server + Database)
python Python/main_async.py --port /dev/ttyACM0
```
*   **Logs**: You should see lines like `[INFO] - DemeterService - Started`.
*   **Data**: When the Node sends data, you'll see `[INFO] - SensorLogger - 2,25.50,60.00`.

---

## 4. Run the GUI (Optional)

Open a **new terminal**, activate the venv, and run the GUI.

```bash
source Python/.venv/bin/activate
python Python/main_gui.py
```
*   Login with the default credentials (e.g., `admin` / `admin` or check `config/users.json`).
*   Or use the **"Bypass (Dev)"** button.

---

## 5. Verification

### A. Check the Database
I created a helper script to verify data is being saved without needing SQL knowledge.

```bash
python Python/scripts/verify_data.py
```
**Output Example:**
```text
✅ Database found: .../demeter_data.db
📊 Total Records: 15
📋 Latest 10 Readings:
ID    Timestamp                 Node  Temp       Hum       
------------------------------------------------------------
15    2026-02-10T15:30:00       2     25.50      60.00     
...
```

### B. Troubleshooting
*   **No Data?**
    *   Check if Gateway LED blinks (receiving ESP-Now).
    *   Check `main_async.py` logs: Is correct UART port used?
    *   Check `pio device monitor`: Is Gateway printing frames?
