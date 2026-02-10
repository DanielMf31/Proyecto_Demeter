# 📋 Product Backlog - Proyecto Demeter

**Vision:** A robust, modular, and easy-to-use IoT irrigation system for green houses (ETSIA) and personal scaling.

## 🌟 Epics & User Stories

### 1. 🚜 Hardware & Firmware (The Field)
*   **[Medium]** **Actuator Control (Pumps/Valves)** `Status: In Progress`
    *   As a user, I want to turn pumps on/off via the system so I can irrigate remotely.
    *   *Constraint:* Must interpret protocol V2 `SET_GPIO` commands.
*   **[High]** **Deep Sleep Optimization** `Status: Planned`
    *   As a maintenance user, I want nodes to sleep when not measuring to save battery (Solar power goal).
*   **[Low]** **LoRa Integration** `Status: Research`
    *   As a user with a large field, I want long-range communication where WiFi fails.
*   **[Medium]** **OTA Updates** `Status: Planned`
    *   As a developer, I want to update node firmware wirelessly to avoid opening waterproof enclosures.

### 2. 🖥️ Software & Interface ( The Brain)
*   **[High]** **Irrigation Scheduler** `Status: Planned`
    *   As a farmer, I want to schedule irrigation (e.g., "Every day at 8:00 AM for 10 mins") so I can automate the process.
*   **[Medium]** **Historical Data Visualization** `Status: In Progress`
    *   As an agronomist, I want to see temperature/humidity graphs on the screen to analyze trends.
*   **[Low]** **User Management** `Status: Planned`
    *   As an admin, I want to restrict settings access so students don't accidentally break the configuration.

### 3. ⚙️ Infrastructure & DevOps
*   **[High]** **Automated CI/CD** `Status: Planned`
    *   As a developer, I want code to be automatically tested and deployed to ensure stability.
*   **[Medium]** **Dockerization** `Status: Planned`
    *   As a sysadmin, I want to deploy the backend/GUI as containers for easy updates.

### 4. 🎓 ETSIA Specifics (The Client)
*   **[High]** **Classroom Deployment** `Status: Next Up`
    *   Deploy RPi + Monitor + Testbench in the workshop.
*   **[Medium]** **Student Playground** `Status: Planned`
    *   Allow students to "plan" irrigation cycles to see how the system reacts.
