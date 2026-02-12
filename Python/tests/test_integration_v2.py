import asyncio
import unittest
import json
import logging
import sys
import os

# Ensure we can import from src
# Assuming script is in Python/tests/
# We need to add Python/src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print(f"Debug: Added {src_path} to sys.path")

from proyecto_demeter.core.async_service import DemeterService
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import TempHumReport, CmdId, Ping

# Mock Transport
class MockAsyncUartTransport:
    def __init__(self):
        self.callback = None
        self.output_buffer = []

    def set_callback(self, callback):
        self.callback = callback

    async def connect(self):
        return True

    async def send(self, data):
        self.output_buffer.append(data)
        return True

    # Simulation method to inject data from "Hardware"
    def simulate_rx(self, data: bytes):
        if self.callback:
            self.callback(data)

class TestDemeterIntegrationV2(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Setup Service in Isolation
        self.service = DemeterService()
        self.service.transport = MockAsyncUartTransport()
        self.service.transport.set_callback(self.service.on_uart_data)
        
        # Mock Clients set
        self.service.clients = set() # Reset
        self.mock_client_writer = MockWriter()
        self.service.clients.add(self.mock_client_writer)
        
        # Silence logs
        logging.disable(logging.CRITICAL)

    async def asyncTearDown(self):
        logging.disable(logging.NOTSET)
        # Ensure tasks are cleaned up if necessary

    async def test_fragmented_uart_frame(self):
        """Test that split frames are correctly reassembled."""
        # Create a valid TempHumReport frame
        protocol = DemeterProtocolV2()
        # report = TempHumReport(target_id=0, node_id=2, temperature=25.5, humidity=60.0)
        # Manually serialize based on protocol (TempHumReport ID = 0x0B)
        # Payload: [T_LSB] [T_MSB] [H_LSB] [H_MSB] (x100)
        t_int = int(25.5 * 100)
        h_int = int(60.0 * 100)
        payload = int(t_int).to_bytes(2, 'little', signed=True) + int(h_int).to_bytes(2, 'little', signed=True)
        frame = protocol._pack_frame_raw(dst_id=0, cmd_id=CmdId.TEMP_HUM_REPORT, payload=payload)
        
        # Confirm frame validity
        parsed = protocol.parse_frame(frame)
        self.assertIsNotNone(parsed)
        
        # Split frame into 3 chunks
        chunk1 = frame[:2] # SYNC, LEN
        chunk2 = frame[2:5] # FLAGS, SRC, DST
        chunk3 = frame[5:] # CMD, PAYLOAD, CRC
        
        # print(f"\nSending Chunk 1: {chunk1.hex()}")
        self.service.transport.simulate_rx(chunk1)
        self.assertEqual(len(self.mock_client_writer.data_written), 0) # No broadcast yet

        # print(f"Sending Chunk 2: {chunk2.hex()}")
        self.service.transport.simulate_rx(chunk2) 
        self.assertEqual(len(self.mock_client_writer.data_written), 0) # Still waiting

        # print(f"Sending Chunk 3: {chunk3.hex()}")
        self.service.transport.simulate_rx(chunk3)
        
        # Allow background task (handle_protocol_command) to run
        await asyncio.sleep(0.2)
        
        # Check Broadcast
        self.assertEqual(len(self.mock_client_writer.data_written), 1)
        # Expecting JSON bytes
        json_msg = self.mock_client_writer.data_written[0].decode().strip()
        # print(f"Broadcasted: {json_msg}")
        
        data = json.loads(json_msg)
        # TempHumReport model has node_id, temperature, humidity
        # Note: target_id logic in AsyncService might not preserve src=0 from manual pack unless protocol parses it so.
        # But payload pack used dst_id=0. Src is part of header (default 0 in _pack_frame_raw if not specified?)
        # Let's check _pack_frame_raw signature: def _pack_frame_raw(self, dst_id, cmd_id, payload, src_id=0, flags=0):
        # So Src=0.
        
        # The node_id in TempHumReport comes from the SOURCE address in the frame (set by _parse_temp_hum_report logic using src_id)
        # Wait, previous DataReport had explicit node_id field in payload? No, V2 usually infers node_id from Source Address for reports.
        # Let's check `protocol_v2.py`:
        # def _parse_temp_hum_report(self, dst, src, payload): 
        #    ... src_id = src ... return TempHumReport(node_id=src_id ...)
        
        self.assertEqual(data["node_id"], 0) # Src was 0
        self.assertEqual(data["temperature"], 25.5)
        self.assertEqual(data["humidity"], 60.0)

    async def test_garbage_handling(self):
        """Test that garbage bytes before SYNC are discarded."""
        garbage = b'\x00\xFF\xAA\xBB'
        protocol = DemeterProtocolV2()
        # Ping frame
        frame = protocol.serialize(Ping(target_id=1))
        
        # Send Garbage + valid sequence
        # Note: logic discards only if it finds SYNC.
        self.service.transport.simulate_rx(garbage + frame)
        
        # Should have found the frame eventually
        # NOTE: protocol_v2 create_ping returns a PING command (cmd_id=0x04).
        # Service only broadcasts DataReport (0x10). PING does not trigger broadcast in current impl.
        # But we can verify rx_buffer is empty (consumed).
        self.assertEqual(len(self.service.rx_buffer), 0)

class MockWriter:
    def __init__(self):
        self.data_written = []
    
    def write(self, data):
        self.data_written.append(data)
    
    def get_extra_info(self, key):
        return ('127.0.0.1', 50000)

    def close(self):
        pass

if __name__ == '__main__':
    unittest.main()
