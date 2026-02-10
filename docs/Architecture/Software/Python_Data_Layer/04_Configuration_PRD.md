# Product Requirements Document (PRD): Centralized Python Configuration

## 1. Overview
The current configuration system is fragmented between `Python/config` (legacy/external) and `src/proyecto_demeter/config`. The goal is to centralize configuration management into a robust, type-safe system using `pydantic-settings` within the package itself (`src/proyecto_demeter/config`), while maintaining external configuration files (e.g., `.env`, `users.json`) in a predictable location.

## 2. Goals
- **Centralization**: Single source of truth for all application settings.
- **Environment Awareness**: Support for `.env` files and environment variable overrides.
- **Path Management**: robust handling of project roots, ensuring `logs/` and `data/` directories are correctly located relative to the application or user data directories.
- **Type Safety**: Use Pydantic models for validation.
- **Backward Compatibility**: Ensure existing modules (`DatabaseManager`, `SensorLogger`) can easily switch to the new config.

## 3. Architecture Design

### 3.1. Directory Structure
We will move the detailed configuration logic INTO the source package to make it self-contained, but keep configuration *files* (data) accessible.

```text
Python/
├── config/                  # External Config Files (UserData)
│   ├── users.json           # User credentials
│   ├── inventory.json       # Product/Device definitions
│   └── settings.yaml        # (Optional) Static overrides
├── .env                     # Secrets / Environment specific vars
└── src/
    └── proyecto_demeter/
        └── config/
            ├── __init__.py  # Exposes 'settings' object
            ├── provider.py  # Implementation of Settings class
            └── constants.py # Fixed constants (Defaults)
```

### 3.2. Configuration Hierarchy (Priority Order)
1.  **Environment Variables** (`DEMETER_DEBUG=true`)
2.  **Secrets File** (`.env`)
3.  **Default Values** (Code-defined in Pydantic models)

### 3.3. Key Configuration Sections
-   **System**: `DEBUG`, `LOG_LEVEL`, `APP_NAME`.
-   **Paths**: Dynamic methods to get `LOGS_DIR`, `DATA_DIR`, `CONFIG_DIR`.
-   **Database**: Connection strings, timeouts.
-   **Server**: Host, Port.
-   **Sensors**: Polling intervals, thresholds.

## 4. Implementation Details

### 4.1. The `Settings` Class
Located in `src/proyecto_demeter/config/provider.py`.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Demeter IoT"
    ENV: str = "development"
    DEBUG: bool = False
    
    # Paths (Computed properties or fields)
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent # Navigate up to Python/
    
    @property
    def LOG_DIR(self) -> Path:
        p = self.BASE_DIR / "logs"
        p.mkdir(exist_ok=True)
        return p

    @property
    def DATA_DIR(self) -> Path:
        p = self.BASE_DIR / "data"
        p.mkdir(exist_ok=True)
        return p
        
    @property
    def CONFIG_DIR(self) -> Path:
        return self.BASE_DIR / "config"

    # Database
    DB_NAME: str = "demeter_data.db"
    
    # ... other sections ...

    model_config = SettingsConfigDict(env_prefix="DEMETER_")
```

### 4.2. Usage
Modules will import a singleton instance:
```python
from proyecto_demeter.config import settings

print(settings.DATA_DIR)
```

## 5. Migration Plan
1.  Create `src/proyecto_demeter/config/provider.py`.
2.  Instantiate `settings` in `src/proyecto_demeter/config/__init__.py`.
3.  Refactor `main_async.py` and `main_gui.py` to use `settings`.
4.  Refactor `SensorLogger` and `DatabaseManager` to accept `settings` derived paths or use the singleton.
5.  Update `test` suit to mock `settings` if necessary.

## 6. Success Criteria
-   `pytest` passes for all tests.
-   Logs appear in `Python/logs/`.
-   Database appears in `Python/data/`.
-   GUI loads `users.json` from `Python/config/`.
