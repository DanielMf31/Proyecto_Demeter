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

### Changed
- **Schema Refactoring**: Consolidated all Pydantic models into `src/proyecto_demeter/config/schemas.py`.
- **UI**: (In Progress) Refactoring to Tabbed Interface.
- **Gateway Firmware**: Updated `main_receptor.cpp` to act as a Bridge (Gateway).

### Removed
- **Legacy Files**: Deleted `protocols/schemas_protocol.py`, `protocols/schemas_sequencer.py`, and old `device_manager.py`.
