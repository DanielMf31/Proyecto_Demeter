import json
import os
from typing import List
from ..shared.schemas import SequenceFile
from ..config import settings

class SequenceManager:
    """
    Handles loading and saving sequences to JSON files.
    """
    def __init__(self, directory: str = None):
        if directory:
            self.directory = directory
        else:
            self.directory = str(settings.SEQUENCES_DIR)
            
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
        if not os.path.exists(self.directory):
            return []
        files = [f for f in os.listdir(self.directory) if f.endswith(".json")]
        return sorted(files)
