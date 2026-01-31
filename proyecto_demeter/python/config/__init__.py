from .settings import Settings
from .config import AppConfig, LLMConfig, OCRConfig, StorageConfig, ValidationConfig

# Instancia global única de configuración
settings = Settings()

# Cargar configuración desde JSON si existe (opcional, para entornos locales)
settings.load_json_overrides()

# Exportar símbolos públicos
__all__ = [
    "settings", 
    "Settings",
    "AppConfig",
    "LLMConfig",
    "OCRConfig",
    "StorageConfig",
    "ValidationConfig"
]
