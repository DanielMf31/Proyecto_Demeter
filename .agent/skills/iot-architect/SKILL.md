---
name: iot-architect
description: Architectural patterns and best practices for robust Internet of Things (IoT) systems, specifically targeting interactions between embedded C++ and high-level Python services.
---

# IoT Architect

This skill focuses on designing resilient, scalable, and maintainable IoT systems given the constraints of embedded hardware and unstable networks.

## Core Concepts

1.  **The "Always Broken" Assumption:** Networks fail, sensors drift, power fluctuates. Design for failure.
2.  **Decoupling:** Separate hardware control (C++) from business logic (Python) and user interface (GUI/Web).
3.  **State Management:** Single Source of Truth vs. Distributed State.
4.  **Protocol Design:** Efficient binary packing vs. verbose JSON/Text (Trade-offs).

## Architecture Patterns

### 1. The Gateway Pattern (Demeter Model)
-   **Edge Device (ESP32):** Dumb executor. Handles real-time I/O.
-   **Gateway (Raspberry Pi):** Smart controller. Handles logic, database, API, and UI.
-   **Communication:** UART/Serial or Local Network (MQTT/TCP).

### 2. Heartbeats & Watchdogs
-   **Layer 1:** Hardware Watchdog (WDT) on ESP32.
-   **Layer 2:** Communication Heartbeat (Ping/Pong) between ESP32 and RPi.
-   **Layer 3:** Service Restarter (Systemd/Docker) on RPi.

### 3. Graceful Degradation
-   If the RPi disconnects, the ESP32 should enter a "Safe Mode" (turn off motors, keep essentials running).
-   If the UI disconnects, the Backend Service keeps running autonomously.

## Implementation Tips

-   **Serial Communication:** Always use framing (Start/End bytes) and Checksums (CRC).
-   **Buffering:** Implement ring buffers for UART data to avoid overflows.
-   **Logging:** Centralize logs on the Gateway (RPi) since embedded flash is limited/slow.
