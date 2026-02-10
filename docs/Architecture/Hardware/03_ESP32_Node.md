# ESP32 Sensor Node V2

**Role:** Remote Sensor and Actuator
**Model:** ESP32-WROOM-32 / S3
**Network ID:** 2 (Configurable)
**Power:** Battery / Solar (Low power design)

## Sensors (Current Prototype)
| Sensor | Type | ESP32 Pin | Function |
| :--- | :--- | :--- | :--- |
| **DHT22** | Digital | GPIO 4 | Ambient Temperature and Humidity. |
| **DS18B20** | 1-Wire | GPIO 5 | Soil Temperature (Precision). |
| **Soil Moisture** | Analog | GPIO 34 | Capacitive/Resistive (ADC). |

## Firmware (main_node.cpp)
- **Modular Architecture:** Uses `ISensor` plugin system for easy sensor addition.
- **Communication:** ESP-Now (Sends only to Gateway, ID 1).
- **Lifecycle:**
    1. Wake up.
    2. Read all registered sensors.
    3. Package data into `DataReport`.
    4. Send to Gateway.
    5. Sleep (Configurable, currently 5s loop for demo).

## Future Capabilities
- **Actuation:** Control relays (Water pumps) via `SET_GPIO` commands.
- **OTA:** Remote firmware updates (Over-The-Air).
