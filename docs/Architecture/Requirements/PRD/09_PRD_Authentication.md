# PRD: GUI Authentication

## 1. Introduction
This feature adds a security layer to the application startup. Users must authenticate with valid credentials before accessing the control interface.

## 2. Features

### 2.1 Login Screen
*   **Startup:** The application must launch a `LoginWindow` before the `MainWindow`.
*   **Inputs:** Username and Password fields.
*   **Validation:**
    *   Credentials are checked against `Python/config/users.json`.
    *   If valid: Login window closes, Main Window and Sequencer Window open.
    *   If invalid: Error message is shown.

### 2.2 User Management (Simple)
*   **Store:** `users.json` (JSON Object where Key=Username, Value=Password).
*   **Security:** Plaintext for MVP (Mock/Prototype phase). Future versions should use hashing.

## 3. Technical Implementation
*   **Class:** `LoginWindow(tk.Toplevel)` (or `tk.Tk` if it's the root).
*   **Workflow:**
    1.  `main.py` initializes `LoginWindow`.
    2.  `LoginWindow` blocks or acts as main loop.
    3.  On success, `on_login_success` callback is triggered.
    4.  `main.py` destroys Login and builds Main App.

## 4. Acceptance Criteria
*   [ ] Application opens with Login Screen.
*   [ ] Correct credentials -> Opens App.
*   [ ] Incorrect credentials -> Shows Error.
*   [ ] `users.json` is read correctly.
