import unittest
import struct
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.protocol_v2 import DemeterProtocolV2, CMD_SET_GPIO, CMD_EXEC_SEQUENCE

class TestProtocolV2(unittest.TestCase):
    
    def setUp(self):
        self.proto = DemeterProtocolV2()

    def test_create_set_gpio(self):
        # Target 10, Pin 4, Val 1
        frame = self.proto.create_set_gpio(10, 4, 1)
        
        # Structure: [SYNC][LEN][FLAGS][SRC][DST][CMD] [PIN][VAL][FLAGS] [CRC]
        # FE 03 01 00 0A 10 04 01 00 CRC
        self.assertEqual(frame[0], 0xFE) # Sync
        self.assertEqual(frame[1], 0x03) # Len (3 bytes payload)
        self.assertEqual(frame[4], 10)   # Dst
        self.assertEqual(frame[5], 0x10) # Cmd
        
        # Verify CRC Logic
        # Data: 03 01 00 0A 10 + 04 01 00
        # Sum: 3+1+0+10+16 + 4+1+0 = 35
        self.assertEqual(frame[-1], 35)

    def test_create_sequence(self):
        steps = [
            {'target': 10, 'cmd': 0x10, 'pin': 4, 'val': 1, 'delay': 5000}
        ]
        frame = self.proto.create_sequence(steps)
        
        # Header + Payload (1 byte count + 8 bytes step) + CRC
        # Payload len = 9
        self.assertEqual(frame[1], 9) 
        self.assertEqual(frame[5], CMD_EXEC_SEQUENCE) # 0x30
        
        # Verify Payload Content
        # Skip Header (6 bytes)
        payload = frame[6:-1]
        count = payload[0]
        self.assertEqual(count, 1)
        
        # Step: Target(1) Cmd(1) Pin(1) Val(1) Delay(4)
        step_bytes = payload[1:]
        self.assertEqual(step_bytes[0], 10) # Target
        self.assertEqual(step_bytes[4:], struct.pack('<I', 5000)) # Delay

    def test_crc_calculation(self):
        # Manual Check
        data = b'\x01\x02\x03'
        crc = self.proto._calculate_crc(data)
        # 1+2+3 = 6
        self.assertEqual(crc, 6)
        
        # Overflow Check
        data_big = b'\xFF\x02' # 255 + 2 = 257. 257 % 256 = 1
        crc_big = self.proto._calculate_crc(data_big)
        self.assertEqual(crc_big, 1)

if __name__ == '__main__':
    unittest.main()
