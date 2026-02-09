# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **ESP-Now Integration**: Full support for ESP-Now communication between Gateway and Node.
    - `EspNowStrategy`: Implementation of `IComms` for ESP-Now.
    - `GatewayStrategy`: Composite strategy handling UART (PC) and ESP-Now (Nodes).
    - `ProtocolEngine`: Added `sendPing` and `ROUTE_ADD` handling.
    - `main_esp_now_1.cpp` & `main_esp_now_2.cpp`: Standalone test sketches for verification.
    - `test_espnow_1` & `test_espnow_2`: New PlatformIO environments for isolated testing.
- **Manual Ping**: Added 'P' command to Serial menu for manual bidirectional PING testing.
- **Hardcoded Routes**: Added MAC address hardcoding in both Firmware and `devices.json` for reliable startup.
- **WiFi Channel Fix**: Forced WiFi Channel 1 in `EspNowStrategy` to prevent channel mismatch on ESP32-S3.

### Changed
- **Refactoring**: `GatewayStrategy` split into `.h` and `.cpp` for better code organization.
- **PlatformIO Config**: Updated `platformio.ini` to include new files and environments.
- **Protocol**: Updated `ProtocolEngine` to correctly parse and route frames based on Destination ID.

### Fixed
- **ESP-Now Initialization**: Fixed `peerInfo` not being zero-initialized, causing add peer failures.
- **Compilation Errors**: Fixed missing includes (`<Arduino.h>`, `<esp_wifi.h>`) in strategy files.
