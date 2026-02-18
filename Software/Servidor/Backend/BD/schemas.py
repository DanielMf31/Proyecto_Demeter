from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict

# --- User Schemas ---
class UserBase(BaseModel):
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
