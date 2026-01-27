import json
import os
import logging

class DeviceManager:
    """
    Manages the registry of known devices, loading from inventory.json.
    Resolves names to IDs and MACs.
    """
    def __init__(self, config_path="Python/config/inventory.json"):
        self.logger = logging.getLogger("DeviceManager")
        self.devices = {}
        self.system_config = {}
        self.config_path = config_path
        self.load_inventory()

    def load_inventory(self):
        """Loads the JSON configuration."""
        if not os.path.exists(self.config_path):
             # Try absolute path if relative fails, or default
             self.logger.error(f"Inventory file not found at: {self.config_path}")
             return

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                self.devices = data.get("devices", {})
                self.system_config = data.get("system", {})
                self.logger.info(f"Loaded {len(self.devices)} devices from inventory.")
        except Exception as e:
            self.logger.error(f"Failed to load inventory: {e}")

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
                continue # Gateway doesn't need to route to itself
            
            node_id = dev["node_id"]
            mac_str = dev.get("mac", "")
            
            # Convert "AA:BB:..." to bytes
            try:
                mac_bytes = bytes.fromhex(mac_str.replace(":", ""))
                if len(mac_bytes) == 6:
                    routes.append((node_id, mac_bytes))
            except ValueError:
                self.logger.warning(f"Invalid MAC for {name}: {mac_str}")
        
        return routes

    def get_gateway_id(self):
        return self.system_config.get("gateway_id", 1)
