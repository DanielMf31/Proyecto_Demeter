import json
import os
import logging

class DeviceManager:
    """
    Manages the registry of known devices AND system configuration.
    Loads from inventory.json.
    Resolves names to IDs and MACs, and provides global settings (ports, etc).
    """
    def __init__(self, config_path="Python/config/inventory.json"):
        self.logger = logging.getLogger("DeviceManager")
        self.devices = {}
        self.system_config = {}
        self.global_config = {}
        self.config_path = config_path
        self.load_inventory()

    def load_inventory(self):
        """Loads the JSON configuration."""
        # Resolve absolute path if needed
        if not os.path.exists(self.config_path):
             # Try looking in absolute path relative to project root
             # This is a fallback
             pass

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.devices = data.get("devices", {})
                self.system_config = data.get("system", {})
                self.global_config = data.get("config", {})
                
                # Apply defaults if config is missing
                self._apply_defaults()
                
                self.logger.info(f"Loaded {len(self.devices)} devices. Config loaded.")
        except Exception as e:
            self.logger.error(f"Failed to load inventory from {self.config_path}: {e}")
            self.devices = {}
            self.global_config = {}
            self._apply_defaults()

    def _apply_defaults(self):
        """Ensures critical config keys exist."""
        defaults = {
            "serial_port": "/dev/serial0",
            "baud_rate": 115200,
            "log_level": "INFO",
            "ui_title": "Demeter System (Default)",
            "ui_geometry": "600x400"
        }
        for key, val in defaults.items():
            if key not in self.global_config:
                self.global_config[key] = val

    def get_config(self, key):
        """Returns a scalar value from the 'config' section."""
        return self.global_config.get(key)

    def get_device(self, name):
        """Returns the full dictionary for a device."""
        return self.devices.get(name)

    def get_target_info(self, name):
        """Returns tuple (node_id, mac_hex_str)."""
        dev = self.devices.get(name)
        if not dev:
            return None
        return (dev["node_id"], dev.get("mac", ""))

    def get_all_routes(self):
        """
        Returns a list of tuples (node_id, mac_bytes) for all remote nodes.
        Used to configure the Gateway's internal routing table.
        """
        routes = []
        for name, dev in self.devices.items():
            if dev.get("type") == "GATEWAY":
                continue # Gateway doesn't need to route to themselves
            
            node_id = dev["node_id"]
            mac_str = dev.get("mac", "")
            
            # Convert "AA:BB:..." to bytes
            try:
                if mac_str:
                    mac_bytes = bytes.fromhex(mac_str.replace(":", ""))
                    if len(mac_bytes) == 6:
                        routes.append((node_id, mac_bytes))
            except ValueError:
                self.logger.warning(f"Invalid MAC for {name}: {mac_str}")
        
        return routes

    def get_gateway_id(self):
        return self.system_config.get("gateway_id", 1)
