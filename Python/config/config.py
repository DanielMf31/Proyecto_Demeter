from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict

class DeviceConfig(BaseModel):
    """Schema base para configuración de hardware."""
    port: str = "/dev/serial0"
    baudrate: int = 115200
    timeout: float = 1.0

class APIResponse(BaseModel):
    """Estándar de respuesta API."""
    success: bool = True
    message: str = "Operation successful"
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class OCRConfig(BaseModel):
    enabled: bool = Field(default=True, description="Activar/Desactivar módulo OCR")
    provider: str = Field(default="tesseract")
    language: str = Field(default="spa")
    dpi: int = Field(default=300)

class ValidationConfig(BaseModel):
    confidence_threshold: float = Field(default=0.75)
    strict_mode: bool = Field(default=False)
    allowed_extensions: list[str] = Field(default_factory=list)

class PathsConfig(BaseModel):
    """
    Definición DE CÓDIGO de la estructura del proyecto.
    El enfoque moderno prioriza 'Defaults en Código' (Convention over Configuration).
    """
    # 1. Rutas Estructurales (Base)
    root: Path = Field(default=Path("."), description="Raíz del proyecto")
    src: Path = Field(default=Path("src"))
    config: Path = Field(default=Path("config"))
    docs: Path = Field(default=Path("docs"))
    
    # 2. Rutas de Datos (Data Lake)
    data: Path = Field(default=Path("data"))
    input_dir: Path = Field(default=Path("data/input"))
    output_dir: Path = Field(default=Path("data/output"))
    processed_dir: Path = Field(default=Path("data/processed"))
    exports_dir: Path = Field(default=Path("data/exports"))
    logs_dir: Path = Field(default=Path("data/logs"))
    
    # 3. Sub-Componentes del Código (Opcional, para reflexión)
    protocols: Path = Field(default=Path("src/proyecto_demeter/protocols"))
    core: Path = Field(default=Path("src/proyecto_demeter/core"))

    model_config = ConfigDict(ignored_types=(property,))

    model_config = ConfigDict(ignored_types=(property,))

def resolve_project_root() -> Path:
    """
    Resuelve la raíz del proyecto buscando marcadores como pyproject.toml o .git.
    Si no encuentra nada, asume que está a 3 niveles (config -> python -> root).
    """
    current = Path(__file__).resolve().parent
    # Buscamos hacia arriba
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
            
    # Fallback seguro: standard cookiecutter structure (config/.. -> python/.. -> root)
    return Path(__file__).resolve().parent.parent.parent    
