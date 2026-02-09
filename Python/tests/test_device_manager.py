import unittest
import os
import json
import sys
from unittest.mock import patch, mock_open

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.core.device_manager import DeviceManager

class TestDeviceManager(unittest.TestCase):

    def setUp(self):
        # Mock Config Data matching new structure
        self.mock_json = {
            "devices": [
                {"id": 0, "mac": "00:00:00:00:00:00", "type": "host"},
                {"id": 1, "mac": "11:11:11:11:11:11", "type": "gateway"},
                {"id": 2, "mac": "22:22:22:22:22:22", "type": "node"}
            ]
        }
        self.json_str = json.dumps(self.mock_json)

    def test_load_valid_config(self):
        with patch("builtins.open", mock_open(read_data=self.json_str)):
            with patch("os.path.exists", return_value=True):
                mgr = DeviceManager("dummy_path.json")
                
                # Check IDs
                self.assertIsNotNone(mgr.get_device_by_id(1))
                self.assertEqual(mgr.get_device_by_id(2)["mac"], "22:22:22:22:22:22")
                
                # Check MAC lookup
                self.assertEqual(mgr.get_id_by_mac("11:11:11:11:11:11"), 1)

    def test_routes_extraction(self):
        with patch("builtins.open", mock_open(read_data=self.json_str)):
             with patch("os.path.exists", return_value=True):
                mgr = DeviceManager("dummy_path.json")
                routes = mgr.get_all_routes()
                
                # Should contain route for ID 2 (Node)
                # Should SKIP ID 0 (Host) and ID 1 (Gateway)
                self.assertEqual(len(routes), 1)
                
                node_id, mac_bytes = routes[0]
                self.assertEqual(node_id, 2)
                self.assertEqual(mac_bytes, b'\x22\x22\x22\x22\x22\x22')

if __name__ == '__main__':
    unittest.main()
