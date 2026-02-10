# PRD: ESP-Now Integration & Device Management

## 1. Objective
Enable bi-directional communication between the Raspberry Pi (Host) and leaf nodes (ESP32) via a Gateway (ESP32) using ESP-Now. Implement a centralized Device Manager on the Host to manage network topology.

## 2. Features

### 2.1 Centralized Schemas
*   Refactor all Pydantic models (`schemas_protocol.py`, `schemas_sequencer.py`) into a single file: `src/proyecto_demeter/config/schemas.py`.
*   Establish a single source of truth for command definitions and data structures.

### 2.2 Device Management (Host)
*   **Config File:** `config/devices.json` containing a list of known devices.
*   **Schema:**
    *   `id`: Unique Protocol ID (0=Host, 1=Gateway, 2+=Nodes).
    *   `mac`: MAC Address (string format "AA:BB:CC:DD:EE:FF").
    *   `type`: "gateway", "sensor_node", "actuator".
    *   `description`: Human-readable name.
    *   `pins`: Dictionary mapping logical names to physical GPIOs (e.g., `{"valve_1": 4}`).
*   **Class:** `DeviceManager`
    *   Loads `devices.json`.
    *   Provides lookup methods (`get_mac_by_id`, `get_id_by_mac`).

### 2.3 Routing Logic (Host -> Gateway)
*   **Initialization:** On startup, the Host sends `CMD_ROUTE_ADD` commands to the Gateway for every registered device in `devices.json`.
*   **Command:** `RouteAdd(node_id, mac_address_bytes)`.
*   **Gateway Responsibility:**
    *   Receive `ROUTE_ADD`.
    *   Add peer to ESP-Now peer list.
    *   Map `node_id` to MAC address in internal routing table.

### 2.4 Forwarding (Gateway -> Node)
*   When Gateway receives a frame destined for `target_id != 1` (and `!= 0`), it looks up the MAC address.
*   If found, forwards the frame via ESP-Now.
*   If not found, sends `NACK` (Error: Route Not Found).

## 3. Workflows

### 3.1 Startup / Route Sync
1.  **Host** starts.
2.  **DeviceManager** loads `devices.json`.
3.  **Host** connects to Gateway (UART).
4.  **Host** iterates devices and sends `RouteAdd` for each Node.
5.  **Gateway** confirms with `ACK`.

### 3.2 Command Execution
1.  **User** clicks "Ping Node 3".
2.  **Host** serializes `Ping(target_id=3)`.
3.  **Host** sends bytes to Gateway.
4.  **Gateway** parses header. `dst=3`.
5.  **Gateway** looks up MAC for ID 3.
6.  **Gateway** sends via ESP-Now.
7.  **Node 3** receives, processes, sends `ACK` to Gateway (ESP-Now).
8.  **Gateway** receives `ACK` (ESP-Now), forwards to **Host** (UART).
