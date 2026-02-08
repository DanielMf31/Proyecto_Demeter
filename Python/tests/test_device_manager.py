import unittest
import os
import json
import sys
from unittest.mock import patch, mock_open

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.protocols.device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        # Mock Config Data
        self.mock_json = {
            "config": {
                "serial_port": "/dev/ttyTEST",
                "baud_rate": 9600
            },
            "devices": {
                "pump1": {"node_id": 10, "pin": 4, "mac": "AA:BB:CC:DD:EE:FF", "type": "RELAY"},
                "sensor1": {"node_id": 20, "mac": "11:22:33:44:55:66", "type": "SENSOR"}
            }
        }
        self.json_str = json.dumps(self.mock_json)

    def test_load_valid_config(self):
        with patch("builtins.open", mock_open(read_data=self.json_str)):
            mgr = DeviceManager("dummy_path.json")
            
            # Check Global Config
            self.assertEqual(mgr.get_config("serial_port"), "/dev/ttyTEST")
            self.assertEqual(mgr.get_config("baud_rate"), 9600)
            
            # Check Device loaded
            self.assertIsNotNone(mgr.get_device("pump1"))
            self.assertEqual(mgr.get_device("pump1")["node_id"], 10)

    def test_default_fallback(self):
        # Test loading a non-existent file
        with patch("os.path.exists", return_value=False):
            mgr = DeviceManager("non_existent.json")
            
            # Should load defaults
            self.assertEqual(mgr.get_config("serial_port"), "/dev/serial0")
            self.assertEqual(mgr.get_config("baud_rate"), 115200)

    def test_route_extraction(self):
        with patch("builtins.open", mock_open(read_data=self.json_str)):
            mgr = DeviceManager("dummy_path.json")
            routes = mgr.get_all_routes()
            
            # Expected: 2 routes
            self.assertEqual(len(routes), 2)
            
            # Verify MAC conversion (Hex String -> Bytes)
            # Pump1: 10 -> AA:BB:CC:DD:EE:FF
            expected_mac = b'\xaa\xbb\xcc\xdd\xee\xff'
            
            # Find tuple with node 10
            route_10 = next((r for r in routes if r[0] == 10), None)
            self.assertIsNotNone(route_10)
            self.assertEqual(route_10[1], expected_mac)

if __name__ == '__main__':
    unittest.main()
