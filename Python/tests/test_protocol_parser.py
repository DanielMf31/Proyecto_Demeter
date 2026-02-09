import unittest
import struct
import sys
import os

# Add src to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, 'src'))

from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2, DataReport, CmdId, HEADER_FMT, SYNC_BYTE
from proyecto_demeter.shared.schemas import DemeterCommand

class TestDemeterProtocolV2(unittest.TestCase):
    def setUp(self):
        self.protocol = DemeterProtocolV2()

    def test_parse_data_report(self):
        """Test parsing of a valid DataReport frame."""
        # Construct a raw frame
        # [SYNC] [LEN] [FLAGS] [SRC] [DST] [CMD] [PAYLOAD] [CRC]
        # Payload for DataReport: T_LSB, T_MSB, H_LSB, H_MSB (4 bytes)
        # Temp = 25.50 -> 2550 (0x09F6) -> F6 09
        # Hum = 60.00 -> 6000 (0x1770) -> 70 17
        
        sync = SYNC_BYTE
        length = 4
        flags = 0
        src = 10 # Node ID
        dst = 1  # Gateway ID
        cmd_id = CmdId.DATA_REPORT
        
        header = struct.pack(HEADER_FMT, sync, length, flags, src, dst, cmd_id)
        payload = struct.pack('<hh', 2550, 6000)
        
        # Calculate CRC
        data_to_hash = header[1:] + payload
        crc = sum(data_to_hash) % 256
        
        frame = header + payload + struct.pack('<B', crc)
        
        # Parse
        cmd = self.protocol.parse_frame(frame)
        
        # Assertions
        self.assertIsNotNone(cmd, "Parsed command should not be None")
        self.assertIsInstance(cmd, DataReport)
        self.assertEqual(cmd.target_id, 1) # This was the missing field causing error
        self.assertEqual(cmd.node_id, 10)
        self.assertAlmostEqual(cmd.temperature, 25.50)
        self.assertAlmostEqual(cmd.humidity, 60.00)

    def test_parse_invalid_crc(self):
        """Test that invalid CRC returns None."""
        sync = SYNC_BYTE
        length = 0
        flags = 0
        src = 0
        dst = 0
        cmd_id = CmdId.PING
        
        header = struct.pack(HEADER_FMT, sync, length, flags, src, dst, cmd_id)
        payload = b''
        crc = 0xFF # Wrong CRC
        
        frame = header + payload + struct.pack('<B', crc)
        
        cmd = self.protocol.parse_frame(frame)
        self.assertIsNone(cmd)

    def test_incomplete_frame(self):
        """Test incomplete frame handling."""
        frame = b'\xFE\x04\x00' # Sync + Len + Flags ... missing rest
        cmd = self.protocol.parse_frame(frame)
        self.assertIsNone(cmd)

if __name__ == '__main__':
    unittest.main()
