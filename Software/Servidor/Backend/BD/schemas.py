from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# --- User Schemas ---
class UserBase(BaseModel):
    """
    Esquema base para la entidad Usuario. 
    Contiene la validación genérica de Pydantic compartida entre creaciones y respuestas.
    """
    username: str
    role: str = "user"
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- Device Schemas ---
class DeviceBase(BaseModel):
    """
    Esquema base para validar y tipar objetos Device (Relés físicos).
    """
    name: str
    device_type: str
    gpio_pin: int

class DeviceCreate(DeviceBase):
    """Schema for creating a new device."""
    # Ensure frontend can send these fields
    name: str
    device_type: str = "GENERIC"
    gpio_pin: int

class DeviceResponse(DeviceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# --- Sequence Step Schemas ---
class SequenceStepBase(BaseModel):
    """
    Representa un paso en el tiempo que dicta una orden a un Device.
    (Ej: `target_state` = True, `duration_seconds` = 60).
    """
    device_id: int
    step_order: int
    target_state: bool
    duration_seconds: int

class SequenceStepCreate(SequenceStepBase):
    pass

class SequenceStepResponse(SequenceStepBase):
    id: int
    sequence_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Sequence Schemas ---
class SequenceBase(BaseModel):
    """
    Esquema Maestro del contenedor de la Secuencia. Agrupa N `SequenceStepBase`.
    """
    name: str

class SequenceCreate(SequenceBase):
    steps: List[SequenceStepBase]

class SequenceResponse(SequenceBase):
    id: int
    created_by: UUID
    created_at: datetime
    steps: List[SequenceStepResponse]
    model_config = ConfigDict(from_attributes=True)

# --- Activity Log Schemas ---
class ActivityLogBase(BaseModel):
    """
    Reglas de validación para la entrada a la bitácora de actividad.
    Permite `device_id` y `description` nulos si la acción fue a nivel de sistema.
    """
    action_type: str
    description: Optional[str] = None
    device_id: Optional[int] = None

class ActivityLogCreate(ActivityLogBase):
    user_id: UUID

class ActivityLogResponse(ActivityLogBase):
    id: int
    timestamp: datetime
    user_id: UUID
    model_config = ConfigDict(from_attributes=True)

# --- LIMS Schemas (Plants & Experiments) ---
class PlantBase(BaseModel):
    """
    Esquema de las Plantas físicas administradas por el sistema (LIMS).
    Garantiza que el front-end siempre envíe la metadata obligatoria (especie, siembra).
    """
    name: str
    identificador_fisico: str
    especie_variedad: str
    fecha_siembra: date
    estado_vital: str = "Activa"
    metadata_cientifica: Dict[str, Any] = {}
    node_id: int

class PlantCreate(PlantBase):
    pass

class PlantUpdate(BaseModel):
    name: Optional[str] = None
    especie_variedad: Optional[str] = None
    fecha_siembra: Optional[date] = None
    estado_vital: Optional[str] = None
    metadata_cientifica: Optional[Dict[str, Any]] = None
    node_id: Optional[int] = None

class PlantResponse(PlantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ExperimentBase(BaseModel):
    """
    Colección de plantas agrupadas conceptualmente bajo un diseño experimental.
    """
    name: str
    description: Optional[str] = None

class ExperimentCreate(ExperimentBase):
    plant_ids: List[int] = []  # IDs chosen in the Frontend Cart 

class ExperimentResponse(ExperimentBase):
    id: int
    created_at: datetime
    user_id: Optional[UUID] = None
    api_key: str
    plants: List[PlantResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
