import json
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from .config import LLMConfig, OCRConfig, ValidationConfig, PathsConfig, DeviceConfig

class Settings(BaseSettings):
    """
    Gestor de configuración global unificado.
    
    Integra PathsConfig (que ahora incluye Storage) y el resto de módulos.
    """
    # Metadatos
    app_name: str = Field(default="Ticket Processor AI", validation_alias="APP_NAME")
    debug: bool = Field(default=False, validation_alias="DEBUG")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Módulos
    llm: LLMConfig = Field(default_factory=LLMConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    device: DeviceConfig = Field(default_factory=DeviceConfig)

    # Rutas y Almacenamiento (Unificado)
    paths: PathsConfig = Field(default_factory=PathsConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__", 
        extra="ignore"
    )
      
    def setup_structure(self) -> None:
        """
        Crea físicamente la estructura de directorios definida en configuración.
        Delega completamente la responsabilidad al FileSystemManager.
        """
        try:
            # Importación dinámica para evitar SyntaxError en la plantilla y ciclos
            import importlib
            # El nombre del paquete se renderizará al generar el proyecto
            pkg = "proyecto_demeter"
            module_name = f"src.{pkg}.core.file_handler"
            
            try:
                module = importlib.import_module(module_name)
                FileSystemManager = module.FileSystemManager
            except ImportError:
                # Fallback para cuando estamos probando la plantilla cruda (opcional o solo raise)
                # Intenta buscar relativo si falla el absoluto renderizado
                raise
            
            # Inicializar manager en la raíz configurada
            manager = FileSystemManager(base_dir=self.paths.root)
            
            print(f"Orchestrating project structure setup in: {self.paths.root.resolve()}")
            
            # Obtener mapa de rutas (Code-First Source of Truth)
            paths_dict = self.paths.model_dump()
            
            # Delegar al Manager
            created = manager.setup_workspace(paths_dict)
            
            print(f"Project structure successfully initialized ({len(created)} directories checked/created).")
            
        except ImportError:
            print("Warning: Could not import FileSystemManager. Are dependencies installed?")
        except Exception as e:
            print(f"Error orchestrating structure: {e}")
