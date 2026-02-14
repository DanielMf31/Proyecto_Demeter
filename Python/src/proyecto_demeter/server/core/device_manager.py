import json
import os
import logging
from typing import Dict, Optional, List, Tuple

class DeviceManager:
    """
    Manages the registry of known devices in the Demeter Network.
    Loads from devices.json.
    """
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("DeviceManager")
        self.devices = []
        self.id_map = {} # id -> device dict
        self.mac_map = {} # mac -> device dict
        
        if config_path is None:
            # Default path: Python/config/devices.json
            # Assumes this file is in src/proyecto_demeter/core/
            base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
            self.config_path = os.path.join(base, "config", "devices.json")
        else:
            self.config_path = config_path
            
        self.load_devices()

    def load_devices(self):
        if not os.path.exists(self.config_path):
            self.logger.warning(f"Device config not found at {self.config_path}")
            return

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)
                self.devices = data.get("devices", [])
                
            # Indexing
            self.id_map = {d["id"]: d for d in self.devices}
            self.mac_map = {d["mac"]: d for d in self.devices}
            
            self.logger.info(f"Loaded {len(self.devices)} devices.")
            
        except Exception as e:
            self.logger.error(f"Failed to load devices: {e}")

    def get_device_by_id(self, node_id: int) -> Optional[Dict]:
        return self.id_map.get(node_id)

    def get_mac_by_id(self, node_id: int) -> Optional[str]:
        dev = self.id_map.get(node_id)
        return dev.get("mac") if dev else None

    def get_id_by_mac(self, mac: str) -> Optional[int]:
        dev = self.mac_map.get(mac)
        return dev.get("id") if dev else None

    def get_all_routes(self) -> List[Tuple[int, bytes]]:
        """
        Returns list of (node_id, mac_bytes) for all nodes EXCEPT Host and Gateway.
        (Gateway knows itself, Host talks to Gateway via UART).
        Actually, Gateway needs to know about other nodes to route TO them.
        """
        routes = []
        for dev in self.devices:
            nid = dev["id"]
            dtype = dev["type"].lower()
            mac_str = dev.get("mac")
            
            # Skip Host (0) and usually Gateway (1) doesn't need a route to itself, 
            # but if there are multiple gateways, it might.
            # For now, we route everything != Gateway(1) and != Host(0)
            if nid in [0, 1]:
                continue
                
            if mac_str:
                try:
                    # Convert AA:BB... to bytes
                    mac_bytes = bytes.fromhex(mac_str.replace(":", ""))
                    routes.append((nid, mac_bytes))
                except ValueError:
                    self.logger.warning(f"Invalid MAC for node {nid}: {mac_str}")
                    
        return routes
