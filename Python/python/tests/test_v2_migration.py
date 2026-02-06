import unittest
import sys
import os

# Add Python root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2, CMD_SET_GPIO
from proyecto_demeter.protocols.device_manager import DeviceManager

class TestProtocolMigration(unittest.TestCase):
    
    def setUp(self):
        self.proto = DemeterProtocolV2()
        # Create a dummy config for testing
        config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config'))
        self.test_config_path = os.path.join(config_dir, "test_inv.json")
        with open(self.test_config_path, "w") as f:
            f.write("""
            {
                "devices": {
                    "test_pump": { "node_id": 10, "mac": "AA:AA:AA:AA:AA:AA", "pin": 4 }
                }
            }
            """)
        self.dev_mgr = DeviceManager(self.test_config_path)

    def tearDown(self):
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)

    def test_packet_generation_set_gpio(self):
        # Human Input: "Turn on Node 10, Pin 4"
        frame = self.proto.create_set_gpio(target_id=10, pin=4, value=1)
        
        # Expected Header: FE(0) 03(1) 01(2) 00(3) 0A(4) 10(5)
        # Expected Payload: 04 01 00
        # Expected CRC: Sum of (Header[1:] + Payload) % 256
        # Data to Hash: 03 01 00 0A 10 + 04 01 00
        # Sum: 3+1+0+10+16 + 4+1+0 = 35 (0x23)
        
        self.assertEqual(len(frame), 10) # 6 Header + 3 Payload + 1 CRC
        self.assertEqual(frame[0], 0xFE) # Sync
        self.assertEqual(frame[4], 10)   # Dst
        self.assertEqual(frame[5], 0x10) # Cmd
        self.assertEqual(frame[-1], 35)  # Auto-calc CRC
        
        print(f"Generated Frame: {frame.hex()}")

    def test_inventory_mac_loading(self):
        node, mac = self.dev_mgr.get_target_info("test_pump")
        self.assertEqual(node, 10)
        self.assertEqual(mac, "AA:AA:AA:AA:AA:AA")
        
        routes = self.dev_mgr.get_all_routes()
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0][0], 10)
        self.assertEqual(routes[0][1], b'\xaa\xaa\xaa\xaa\xaa\xaa')

    def test_sequence_generation(self):
        steps = [
            {'target': 10, 'cmd': CMD_SET_GPIO, 'pin': 4, 'val': 1, 'delay': 5000},
            {'target': 11, 'cmd': CMD_SET_GPIO, 'pin': 5, 'val': 0, 'delay': 0}
        ]
        frame = self.proto.create_sequence(steps)
        
        # Header: Len should be 1 + 8 + 8 = 17 bytes
        self.assertEqual(frame[1], 17) 
        self.assertEqual(frame[5], 0x30) # CMD_EXEC_SEQUENCE

if __name__ == '__main__':
    unittest.main()
