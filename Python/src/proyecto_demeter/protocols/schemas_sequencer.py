from pydantic import BaseModel, Field
from typing import List

class SequenceStep(BaseModel):
    """
    Represents a single step in a timed sequence.
    """
    pin: int = Field(..., ge=4, le=7, description="GPIO Pin Number (4-7)")
    value: int = Field(..., ge=0, le=1, description="Logic Level (0=LOW, 1=HIGH)")
    delay_ms: int = Field(..., gt=0, description="Duration in milliseconds to wait AFTER this step")

class SequenceList(BaseModel):
    """
    Container for validating a full sequence.
    """
    steps: List[SequenceStep]
