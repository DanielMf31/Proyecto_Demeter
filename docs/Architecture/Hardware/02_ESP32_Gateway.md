# ESP32 Gateway (Bridge)

**Role:** Transparent Bridge between Wireless Sensor Network and Central Server
**Model:** ESP32-WROOM-32 / S3
**Network ID:** 1 (Master)

## Connectivity
- **UART2 (GPIO 16 RX / 17 TX):** Wired connection to Raspberry Pi.
- **ESP-Now (WiFi 2.4GHz):** Proprietary wireless link with Nodes.

## Firmware (main_gateway.cpp)
- **Protocol:** Demeter V2 (Binary).
- **Strategy:** Hybrid (UART + ESP-Now). Receives from one interface, forwards to the other.
- **Execution Modes:**
    - **Immediate:** Forwards commands instantly.
    - **Queue:** Buffers commands if the network is busy (Experimental).
- **Debug:** Interactive menu via USB Serial (115200) for manual testing ('H' ping host, 'P' ping node).
