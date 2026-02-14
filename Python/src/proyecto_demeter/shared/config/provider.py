try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic.v1 import BaseSettings
    # Mock SettingsConfigDict for V1 if needed or just ignore
    SettingsConfigDict = lambda **kwargs: kwargs
from pathlib import Path
from pydantic import Field
import os

class Settings(BaseSettings):
    """
    Unified Configuration Provider for Proyecto Demeter.
    
    Priority:
    1. Environment Variables (DEMETER_*)
    2. .env file
    3. Defaults
    """
    # ==========================================
    # 1. System Metadata
    # ==========================================
    APP_NAME: str = "Demeter IoT"
    ENV: str = "development"
    DEBUG: bool = False
    
    # ==========================================
    # 2. Paths (Calculated relative to this file)
    # ==========================================
    # Assumes this file is in Python/src/proyecto_demeter/shared/config/provider.py
    # We want BASE_DIR to be Python/
    # .parent -> config
    # .parent -> shared
    # .parent -> proyecto_demeter
    # .parent -> src
    # .parent -> Python
    _PROJ_ROOT: Path = Path(__file__).resolve().parent.parent.parent.parent.parent
    
    @property
    def BASE_DIR(self) -> Path:
        return self._PROJ_ROOT

    @property
    def LOG_DIR(self) -> Path:
        """Centralized Logs Directory (Python/logs)"""
        p = self.BASE_DIR / "logs"
        p.mkdir(exist_ok=True)
        return p

    @property
    def DATA_DIR(self) -> Path:
        """Centralized Data Directory (Python/data)"""
        p = self.BASE_DIR / "data"
        p.mkdir(exist_ok=True)
        return p
        
    @property
    def CONFIG_DIR(self) -> Path:
        """External Config Directory (Python/config)"""
        p = self.BASE_DIR / "config"
        return p

    @property
    def SEQUENCES_DIR(self) -> Path:
        """Sequence Files Directory (Python/config/sequences)"""
        p = self.CONFIG_DIR / "sequences"
        p.mkdir(parents=True, exist_ok=True)
        return p

    # ==========================================
    # 3. Component Configs
    # ==========================================
    # Database
    DB_NAME: str = "demeter_data.db"
    
    @property
    def DB_PATH(self) -> str:
        return str(self.DATA_DIR / self.DB_NAME)

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "demeter_service.log"
    
    @property
    def LOG_FILE_PATH(self) -> str:
        return str(self.LOG_DIR / self.LOG_FILE)

    # Server
    HOST: str = "0.0.0.0"
    PORT: str = "/dev/serial0"
    SOCKET_PORT: int = 8888
    MOCK_MODE: str = "MIXED"
    MOCK: bool = False

    # V2 Config
    model_config = SettingsConfigDict(
        env_prefix="DEMETER_",
        env_file=".env",
        extra="ignore"
    )

    # V1 Config removed to avoid PydanticUserError: "Config" and "model_config" cannot be used together
    # class Config:
    #     env_prefix = "DEMETER_"
    #     env_file = ".env"
    #     extra = "ignore"

# Singleton Instance
settings = Settings()
