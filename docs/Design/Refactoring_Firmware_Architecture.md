# Firmware Architecture Refactoring Design

## Overview
This document outlines the design for refactoring the Demeter Firmware architecture to improve synchronization, protocol reliability, and code organization. The primary goal is to transition from `SystemContext` to a more robust `SystemManager` that handles protocol states and system actions centrally.

## Core Concepts

### 1. SystemManager (formerly SystemContext)
The `SystemManager` will be the central orchestrator of the firmware. It will manage the system's state machine, handling the transition between initialization, connection (handshake), and operation.

**Responsibilities:**
*   **State Management:** Tracks the current state of the system (e.g., `BOOT`, `HANDSHAKE`, `IDLE`, `RUNNING`, `ERROR`).
*   **Protocol Logic:** Implements the high-level protocol flow (Handshake, Data Transfer, Reporting) using the underlying `ProtocolEngine`.
*   **Action Execution:** Centralizes the logic for executing system actions like sending reports or processing received commands.
*   **Component Coordination:** Coordinates interactions between `ProtocolEngine`, `GpioController`, and `SensorManager`.

### 2. ProtocolEngine & Handshake
The `ProtocolEngine` remains the mechanism for framing and dispatching messages. The `SystemManager` implements the policy.

**New Handshake Protocol:**
To ensure robust connectivity over both UART and ESP-Now, a 3-way handshake will be implemented:
1.  **SYN (Synchronize):** Initiator (usually a Node or Gateway) sends `SYN` to request connection.
2.  **SYN-ACK (Synchronize-Acknowledge):** Receiver responds with `SYN-ACK` to confirm readiness.
3.  **ACK (Acknowledge):** Initiator confirms connection with `ACK`.

**Protocol States:**
*   `DISCONNECTED`: No active connection.
*   `WAITING_SYN_ACK`: Sent `SYN`, waiting for response.
*   `WAITING_ACK`: Sent `SYN-ACK`, waiting for final confirmation.
*   `CONNECTED`: Handshake complete, ready for data.

### 3. Node Simplification
The `Node` classes (`Node_Sensor`, `Node_Actuator`, `Node_Gateway`) will be simplified to focus on hardware-specific initialization and interface logic.

**Changes:**
*   **`setup()`:** A simple method to initialize the `SystemManager` and hardware.
*   **`loop()` / `update()`:** Delegates core logic to `SystemManager`.
*   **Command Interface:** The `Node` class will handle user interaction (e.g., Serial commands). For example, a button press on the Node can trigger a Handshake sequence via the `SystemManager`.

### 4. Shared Pin Configuration
To ensure consistency across the project, pin definitions will be standardized in `PinConfig.h` or within the Node definitions.
*   **UART:** Pins 16 (RX) and 17 (TX) will be fixed for all nodes.

## detailed Implementation Design

### Class: SystemManager
```cpp
class SystemManager {
public:
    enum class State {
        BOOT,
        HANDSHAKE_SEND_SYN,
        HANDSHAKE_WAIT_SYN_ACK,
        HANDSHAKE_SEND_ACK,
        IDLE,
        RUNNING,
        ERROR
    };

    SystemManager(ProtocolEngine* engine, GpioController* specific_controller...);
    
    void setup();
    void update(); // Main State Machine Loop

    // Actions
    void initiateHandshake(uint8_t targetId);
    void sendData(uint8_t targetId, ...);
    void sendReport(uint8_t targetId, ...);

private:
    State _currentState;
    ProtocolEngine* _engine;
    
    // Internal State Machine Handlers
    void handleHandshakeLogic();
    void handleRunningLogic();
};
```

### Protocol Updates
1.  **New Command IDs:**
    *   `SYN` (0x04)
    *   `SYN_ACK` (0x05)
2.  **Callbacks:**
    *   `_onSynRecv`
    *   `_onSynAckRecv`

### Pattern Usage
*   **State Pattern:** explicit `SystemState` enum and handler methods.
*   **Observer Pattern:** `ProtocolEngine` notifies `SystemManager` via callbacks.
*   **Facade Pattern:** `SystemManager` provides a simplified interface for `Node` to interact with complex subsystems.

## Validating the Architecture
1.  **Unit Tests:** Verify State Machine transitions in `SystemManager` (mocking `ProtocolEngine`).
2.  **Integration Tests:** Simulate Handshake between two instances (Node A and Node B).
3.  **HIL / Manual:** Verify LED feedback on Actuator Node when Handshake completes.
