from pydantic import BaseModel, Field
from typing import List

class SequenceStep(BaseModel):
    """
    Represents a single step in a timed sequence.
    """
    pin: int = Field(..., ge=4, le=7, description="GPIO Pin Number (4-7)")
    value: int = Field(..., ge=0, le=1, description="Logic Level (0=LOW, 1=HIGH)")
    delay_ms: int = Field(..., gt=0, description="Duration in milliseconds to wait AFTER this step")

class SequenceFile(BaseModel):
    """
    Metadata and content for a saved sequence file.
    """
    name: str = Field(..., min_length=1, description="Display Name")
    description: str = Field("", description="Optional Description")
    steps: List[SequenceStep]

import json
import os

class SequenceManager:
    """
    Handles loading and saving sequences to JSON files.
    """
    def __init__(self, directory: str = "sequences"):
        self.directory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), directory)
        os.makedirs(self.directory, exist_ok=True)

    def save_sequence(self, filename: str, sequence: SequenceFile) -> str:
        if not filename.endswith(".json"):
            filename += ".json"
        
        path = os.path.join(self.directory, filename)
        with open(path, "w") as f:
            f.write(sequence.model_dump_json(indent=2))
        return path

    def load_sequence(self, filename: str) -> SequenceFile:
        path = os.path.join(self.directory, filename)
        with open(path, "r") as f:
            data = json.load(f)
        return SequenceFile(**data)

    def list_sequences(self) -> List[str]:
        files = [f for f in os.listdir(self.directory) if f.endswith(".json")]
        return sorted(files)
