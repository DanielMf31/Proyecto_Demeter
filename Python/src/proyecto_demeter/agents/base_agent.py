from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    Clase base para Agentes Inteligentes.
    Solo se incluye si cookiecutter.include_agents == 'yes'.
    """
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config

    @abstractmethod
    def run(self, input_data: Any) -> Any:
        pass

    def log(self, message: str):
        print(f"[AGENT:{self.name}] {message}")
