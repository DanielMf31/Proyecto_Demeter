from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
import os
import logging

class Settings(BaseSettings):
    """
    Unified Configuration Provider for Proyecto Demeter (Raspberry & Backend).
    """
    # ==========================================
    # 1. System Metadata
    # ==========================================
    APP_NAME: str = "Demeter IoT System"
    ENV: str = "development"
    DEBUG: bool = True
    
    # ==========================================
    # 2. Paths (Calculated relative to PROJECT ROOT)
    # ==========================================
    # Assumes structure:
    # Software/Common/configuration.py
    # Software/Servidor
    # Software/Raspberry
    # Base Dir = Software/
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    @property
    def LOG_DIR(self) -> Path:
        p = self.BASE_DIR / "logs"
        p.mkdir(exist_ok=True, parents=True)
        return p
        
    @property
    def DATA_DIR(self) -> Path:
        p = self.BASE_DIR / "data"
        p.mkdir(exist_ok=True, parents=True)
        return p

    # ==========================================
    # 3. Logging
    # ==========================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "demeter_system.log"
    
    @property
    def LOG_FILE_PATH(self) -> str:
        return str(self.LOG_DIR / self.LOG_FILE)

    # ==========================================
    # 4. Database (Raspberry SQLite)
    # ==========================================
    DB_NAME: str = "demeter_local.db"
    
    @property
    def DB_PATH(self) -> str:
        return str(self.DATA_DIR / self.DB_NAME)

    # ==========================================
    # 5. Database & External Services
    # ==========================================
    # Backend Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "demeter_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # ==========================================
    # 6. Network / API
    # ==========================================
    HOST: str = "0.0.0.0" # Bind Host
    SOCKET_PORT: int = 8000 # Backend Port
    API_PREFIX: str = "/api"

    # Connectivity (for Raspberry → Server)
    BACKEND_URL: str = "localhost"
    BACKEND_PORT: int = 80

    # ==========================================
    # 7. Hardware (Raspberry UART)
    # ==========================================
    PORT: str = "/dev/serial0" # Default UART
    UART_BAUD: int = 115200
    
    # ==========================================
    # 8. Config
    # ==========================================
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_prefix="DEMETER_"
    )

# Singleton
settings = Settings()
