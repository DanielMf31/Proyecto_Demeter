import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class DeviceManager:
    """
    Handles hardware abstraction on the Raspberry Pi.
    Maps logical device identifiers (pumps/valves from UI) to physical
    node IDs and pin numbers.
    """
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("DeviceManager")
        if config_path is None:
            config_path = str(Path(__file__).parent / "devices.json")
        
        self.config_path = config_path
        self.mappings: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> bool:
        """Loads and parses the devices.json configuration file."""
        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.mappings = data.get("devices", {})
                self.logger.info(f"Loaded {sum(len(v) for v in self.mappings.values())} device mappings.")
                return True
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config: {e}")
        except Exception as e:
            self.logger.error(f"Error loading device config: {e}")
        
        self.mappings = {}
        return False

    def get_config(self) -> Dict[str, Any]:
        """Returns the full device mapping configuration."""
        return self.mappings

    def get_physical_mapping(self, device_type: str, logical_id: str) -> Optional[Tuple[int, int]]:
        """
        Translates a logical device (e.g., 'pump', '1') to its physical
        (target_id, physical_pin) tuple.
        """
        # Frontend might send IDs as strings or ints, handle both
        logical_id = str(logical_id)
        
        # Check if type exists
        type_mapping = self.mappings.get(device_type)
        if not type_mapping:
            self.logger.warning(f"Device type '{device_type}' not found in configuration.")
            return None
            
        # Check if ID exists
        mapping = type_mapping.get(logical_id)
        if not mapping:
            self.logger.warning(f"Logical ID '{logical_id}' for type '{device_type}' not found.")
            return None
            
        target_id = mapping.get("target_id")
        physical_pin = mapping.get("physical_pin")
        
        if target_id is None or physical_pin is None:
            self.logger.error(f"Incomplete mapping for {device_type}:{logical_id}")
            return None
            
        return (target_id, physical_pin)

    def translate_pin(self, logical_pin: int) -> Tuple[int, int]:
        """
        Fallback/Legacy method if only a raw pin index is provided.
        Decides if it's a pump or valve based on heuristics if needed,
        but explicit device_type + ID is preferred.
        """
        # Current PIN_MAP in cards.ts:
        # pump: 1, 2, 3, 4
        # valve: 5, 6, 7, 8
        if 1 <= logical_pin <= 4:
            mapping = self.get_physical_mapping("pump", str(logical_pin))
            if mapping: return mapping
        elif 5 <= logical_pin <= 8:
            mapping = self.get_physical_mapping("valve", str(logical_pin - 4))
            if mapping: return mapping
            
        # Default fallback: return as-is for Gateway (Nodo 1)
        return (1, logical_pin)
