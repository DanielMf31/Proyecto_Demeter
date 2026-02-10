# PRD: Sequencer Persistence & Enhanced UI

## 1. Introduction
This Product Requirements Document (PRD) outlines the improvements for the GUI Sequencer feature in Proyecto Demeter. The goal is to allow users to save and load actuator sequences from JSON files and to improve the visual presentation of the sequence editor.

## 2. Features

### 2.1 Sequence Persistence (JSON)
*   **Requirement:** Users must be able to save the current list of steps to a named file.
*   **Format:** JSON.
*   **Structure:**
    ```json
    {
      "name": "My Morning Routine",
      "description": "Turns on pump and lights",
      "steps": [
        {"pin": 4, "value": 1, "delay_ms": 1000},
        {"pin": 4, "value": 0, "delay_ms": 500}
      ]
    }
    ```
*   **Storage Location:** `Python/sequences/` (default directory).

### 2.2 UI Enhancements (DataGrid)
*   **Requirement:** The list of steps should resemble a structured table (DataGrid) rather than a plain white box.
*   **Details:**
    *   Visible column headers.
    *   Alternating row colors (striped rows) for readability.
    *   Clear separation of columns (Pin, Action, Duration).
    *   "Save" and "Load" buttons in the action area.

### 2.3 Expanded Test Coverage
*   **Requirement:** Verify all Protocol V2 message types.
*   **Scope:**
    *   `CMD_PING` / `RSP_PONG`
    *   `CMD_SET_GPIO` / `RSP_ACK`
    *   `CMD_EXEC_SEQUENCE`
    *   JSON Serialization/Deserialization.

## 3. Technical Implementation
*   **Language:** Python 3.12+ (Tkinter).
*   **Libraries:** `json` (standard lib), `pydantic` (for validation).
*   **Classes:**
    *   `SequencerManager`: Handles file I/O and validation.
    *   `SequencerWindow`: Updates to `Treeview` styles and button handlers.

## 4. Acceptance Criteria
*   [ ] Can save a sequence to `sequences/test.json`.
*   [ ] Can load `sequences/test.json` and see steps populate the UI.
*   [ ] UI table has striped rows and clear headers.
*   [ ] `pytest` passes for new persistence logic and expanded protocol tests.
*   [ ] Main log creates a new session file on restart.
