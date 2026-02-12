# ⚙️ Python Configuration System

> **Status**: Implemented in `v2.1`
> **Provider**: `src.proyecto_demeter.config.provider.Settings`

The Demeter Python backend uses a **Centralized Configuration System** powered by `pydantic-settings`. This ensures type safety, environment variable support, and consistent directory management across the entire application.

## 1. Directory Structure

 The system automatically enforces the following structure relative to the project root (`Python/`):

| Type | Directory | Description | Access in Code |
| :--- | :--- | :--- | :--- |
| **Logs** | `Python/logs/` | Application logs (rotated). | `settings.LOG_DIR` |
| **Data** | `Python/data/` | SQLite database (`demeter_data.db`). | `settings.DATA_DIR` |
| **Config** | `Python/config/` | User files (`users.json`, `inventory.json`). | `settings.CONFIG_DIR` |
| **Source** | `Python/src/` | Application source code. | `settings.BASE_DIR` |

**✅ Yes, the system knows exactly where to save data.** The `Settings` class automatically creates `logs/` and `data/` directories when accessed if they don't exist.

## 2. Usage in Code

Do not hardcode paths. Import the singleton `settings` object.

```python
from proyecto_demeter.config import settings

def save_file(filename):
    # GOOD: Automatically goes to Python/data/myfile.txt
    path = settings.DATA_DIR / filename 
    
    # Check debug mode
    if settings.DEBUG:
        print(f"Saving to {path}")
```

## 3. Configuration Priority

Settings are resolved in the following order (highest priority first):

1.  **Environment Variables**: Prefix with `DEMETER_`.
    *   Example: `export DEMETER_PORT=/dev/ttyUSB1` overrides the default port.
    *   Example: `export DEMETER_DEBUG=true` enables debug mode.
2.  **`.env` File**: A file named `.env` in the `Python/` directory.
    ```ini
    DEMETER_HOST=192.168.1.50
    DEMETER_LOG_LEVEL=DEBUG
    ```
3.  **Default Values**: Defined in `src/proyecto_demeter/config/provider.py`.

## 4. Key Settings

| Setting | Env Variable | Default | Description |
| :--- | :--- | :--- | :--- |
| `APP_NAME` | `DEMETER_APP_NAME` | "Demeter IoT" | Application identifier. |
| `DEBUG` | `DEMETER_DEBUG` | `False` | Enable verbose output. |
| `PORT` | `DEMETER_PORT` | `/dev/serial0` | UART Port for Gateway. |
| `HOST` | `DEMETER_HOST` | `0.0.0.0` | Socket/TCP Server Host. |
| `SOCKET_PORT` | `DEMETER_SOCKET_PORT` | `8888` | Socket/TCP Server Port. |
| `DB_NAME` | `DEMETER_DB_NAME` | `demeter_data.db` | SQLite filename. |

## 5. Adding New Settings

To add a new configuration option:
1.  Open `Python/src/proyecto_demeter/config/provider.py`.
2.  Add a type-hinted field to the `Settings` class.
    ```python
    class Settings(BaseSettings):
        # ... existing ...
        NEW_FEATURE_ENABLED: bool = False
    ```
3.  It is immediately available as `settings.NEW_FEATURE_ENABLED` and configurable via `DEMETER_NEW_FEATURE_ENABLED`.
