import json
import os
from typing import List
from ..config.schemas import SequenceFile

class SequenceManager:
    """
    Handles loading and saving sequences to JSON files.
    """
    def __init__(self, directory: str = "sequences"):
        # Directory logic: If relative, relative to project root (assumed 2 levels up from src/package/core)
        # Main is in Python/
        # src is in Python/src
        # this file is Python/src/proyecto_demeter/core/sequence_manager.py
        # Project root relative to this file: ../../../../
        
        # Better: use the directory passed or default relative to CWD if running from Python/
        self.directory = directory
        if not os.path.isabs(directory):
             # Just use local sequences folder for now, or adhere to previous logic
             # Previous logic: os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + directory
             # That was from schemas_sequencer.py in protocols/
             # Let's keep it simple: relative to execution CWD usually works best for scripts, 
             # but to match previous behavior:
             base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
             self.directory = os.path.join(base, directory)

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
