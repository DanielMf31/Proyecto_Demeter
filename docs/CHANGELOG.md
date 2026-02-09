# Changelog

All notable changes to the "Proyecto Demeter" will be documented in this file.

## [Unreleased]

### Added
- **ESP-Now Integration**: Protocol V2 now supports ESP-Now for communication between Gateway and Nodes.
- **Device Management**: New `DeviceManager` class to handle network topology from `config/devices.json`.
- **Routing**: Implemented `RouteAdd` command to sync routing tables from Host to Gateway.
- **Firmware Strategies**: Added `EspNowStrategy` and `GatewayStrategy` (Composite UART+ESP-Now).
- **Packet Forwarding**: `ProtocolEngine` now forwards packets to destination nodes if not addressed to self.
- **Node Firmware**: Created `main_node.cpp` for remote sensor nodes.
- **Data Transfer**: Implemented `CMD_DATA_REPORT` (0x0B) for telemetry (Temp/Hum) from Node to Gateway to Python.
- **RPi UART Tools**: Added `scripts/setup_rpi_uart.sh` and `scripts/test_uart_loopback.py` for Raspberry Pi configuration.

### Fixed
- **UART Communication**: Implemented Ring Buffer in `UartTransport.py` to handle stream fragmentation and ensure reliable frame reception.
- **ProtocolEngine**: Fixed linker error due to duplicate callback declaration.
- **Python Schemas**: Fixed Pydantic validation error in `RouteAdd` command.

### Changed
- **Schema Refactoring**: Consolidated all Pydantic models into `src/proyecto_demeter/config/schemas.py`.
- **UI**: (In Progress) Refactoring to Tabbed Interface.
- **Gateway Firmware**: Updated `main_receptor.cpp` to act as a Bridge (Gateway).

### Removed
- **Legacy Files**: Deleted `protocols/schemas_protocol.py`, `protocols/schemas_sequencer.py`, and old `device_manager.py`.
