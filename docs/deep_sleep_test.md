# Deep Sleep Test: Sensor Cluster End-to-End

Validates that the ESP32-S3 sensor cluster node can wake from deep sleep, read sensors, send a `SENSOR_CLUSTER_REPORT` (0x0E) to the gateway, and go back to sleep on a 60-second cycle.

## Data flow

```
ESP32 Sensor (deep sleep → wake → read → ESP-NOW)
    → ESP32 Gateway (ESP-NOW → UART rewrite target_id=0)
    → RPi (UART → parse 0x0E → SQLite soil_readings + CSV)
```

## Hardware requirements

| Item | Role |
|------|------|
| ESP32-S3 #1 | Gateway node (ID 1) — connected to RPi via UART (`/dev/serial0`) |
| ESP32-S3 #2 | Sensor cluster node (ID 2) — DS18B20 + capacitive sensors |
| Raspberry Pi | Edge server — receives UART frames, caches to SQLite/CSV |
| DS18B20 | Temperature sensor on GPIO 4 (plant 1) and/or GPIO 6 (plant 2) |
| Capacitive soil sensor | Analog on GPIO 5 (plant 1) and/or GPIO 7 (plant 2) |

### Wiring — Sensor node (ESP32-S3 #2)

| Signal | GPIO |
|--------|------|
| Plant 1 soil capacitive | 4 |
| Plant 1 DS18B20 data | 5 |
| Plant 2 soil capacitive | 6 |
| Plant 2 DS18B20 data | 7 |

Plants are auto-detected — if a DS18B20 fails init, that plant pair is skipped.

### Wiring — Gateway ↔ RPi UART

| RPi | ESP32-S3 Gateway |
|-----|------------------|
| TX (GPIO 14) | RX (GPIO 44) |
| RX (GPIO 15) | TX (GPIO 43) |
| GND | GND |

## Setup and flashing

```bash
# Clone and enter repo
git clone <repo-url> && cd Proyecto_Demeter

# Flash gateway (ESP32-S3 #1 connected via USB)
cd Firmware
pio run -e gateway -t upload

# Flash sensor cluster (swap USB to ESP32-S3 #2)
pio run -e sensor_cluster -t upload
```

## Running the test

### 1. Start RPi edge server (local mode)

```bash
cd Software/Raspberry
PYTHONPATH=src:../Common python src/proyecto_demeter/Hardware/orchestration/edge_server.py
```

### 2. Monitor serial output (optional)

In separate terminals:

```bash
# Sensor cluster node
pio device monitor -b 115200 -p /dev/ttyACM1

# Gateway node
pio device monitor -b 115200 -p /dev/ttyACM0
```

### 3. Expected output

**Sensor node** (repeats every ~60 s):

```
========================================
  DEMETER - Sensor Cluster Node
  Node ID: 2 | Plants: 2
  WAKE UP reason: TIMER
========================================

  Plant 1 (T:GPIO4 S:GPIO5): OK
  Plant 2 (T:GPIO6 S:GPIO7): SKIP (sensor missing)

1/2 plants active.

[Plant 1] Temp: 22.50 C | Soil: 65%
>> Sent SENSOR_CLUSTER_REPORT (1 entries) to Gateway
>> Entering deep sleep for 60 s...
```

**Gateway** (each time the sensor wakes):

```
[CLUSTER] Node 2: 1 entries → forwarding to UART (target_id=0)
```

**RPi logs**:

```
sensor_cluster_report from node 2: 1 entries
Saved cluster reading to soil_readings
```

## Verification

### Check SQLite

```bash
sqlite3 data/demeter_local.db "SELECT * FROM soil_readings ORDER BY id DESC LIMIT 5;"
```

### Check CSV

```bash
ls data/csv/telemetry_*.csv
tail -5 data/csv/telemetry_*.csv
```

### Confirm 60-second cycle

Watch the sensor serial monitor — each wake-up should appear ~60 seconds after the previous one. The first wake-up shows `POWER_ON / RESET`; subsequent ones show `TIMER`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Sensor never wakes | Check power supply — deep sleep current is ~10 uA; USB should keep it powered |
| Gateway doesn't receive | Verify `GATEWAY_MAC` in `main_sensor_cluster.cpp` matches the actual MAC of your gateway ESP32 (`pio device list`) |
| RPi doesn't log anything | Check UART wiring (TX↔RX crossed) and baud rate (115200) |
| "SKIP (sensor missing)" for all plants | DS18B20 needs a 4.7k pull-up on the data line |

## Adjusting sleep duration

Edit `SLEEP_DURATION_S` in `Firmware/src/main_sensor_cluster.cpp`:

```cpp
static constexpr uint64_t SLEEP_DURATION_S = 60;  // change to desired seconds
```

Rebuild and flash: `pio run -e sensor_cluster -t upload`
