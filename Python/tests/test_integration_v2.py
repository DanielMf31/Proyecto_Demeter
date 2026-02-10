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
from proyecto_demeter.shared.schemas import DataReport

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
        self.mock_client_writer = MockWriter()
        self.service.clients.add(self.mock_client_writer)
        
        # Silence logs
        logging.disable(logging.CRITICAL)

    async def asyncTearDown(self):
        logging.disable(logging.NOTSET)
        # Ensure tasks are cleaned up if necessary

    async def test_fragmented_uart_frame(self):
        """Test that split frames are correctly reassembled."""
        # Create a valid DataReport frame
        protocol = DemeterProtocolV2()
        report = DataReport(target_id=0, node_id=2, temperature=25.5, humidity=60.0)
        # Manually serialize based on protocol (DataReport ID = 0x10)
        # Payload: [T_LSB] [T_MSB] [H_LSB] [H_MSB] (x100)
        t_int = int(25.5 * 100)
        h_int = int(60.0 * 100)
        payload = int(t_int).to_bytes(2, 'little', signed=True) + int(h_int).to_bytes(2, 'little', signed=True)
        frame = protocol._pack_frame_raw(dst_id=0, cmd_id=0x0B, payload=payload)
        
        # Confirm frame validity
        parsed = protocol.parse_frame(frame)
        self.assertIsNotNone(parsed)
        
        # Split frame into 3 chunks
        chunk1 = frame[:2] # SYNC, LEN
        chunk2 = frame[2:5] # FLAGS, SRC, DST
        chunk3 = frame[5:] # CMD, PAYLOAD, CRC
        
        print(f"\nSending Chunk 1: {chunk1.hex()}")
        self.service.transport.simulate_rx(chunk1)
        self.assertEqual(len(self.service.clients), 1)
        self.assertEqual(len(self.mock_client_writer.data_written), 0) # No broadcast yet

        print(f"Sending Chunk 2: {chunk2.hex()}")
        self.service.transport.simulate_rx(chunk2) 
        self.assertEqual(len(self.mock_client_writer.data_written), 0) # Still waiting

        print(f"Sending Chunk 3: {chunk3.hex()}")
        self.service.transport.simulate_rx(chunk3)
        
        # Allow background task (handle_protocol_command) to run
        await asyncio.sleep(0.2)
        
        # Check Broadcast
        self.assertEqual(len(self.mock_client_writer.data_written), 1)
        json_msg = self.mock_client_writer.data_written[0].decode()
        print(f"Broadcasted: {json_msg}")
        
        data = json.loads(json_msg)
        self.assertEqual(data["node_id"], 0) # Src was 0 in _pack_frame_raw default
        self.assertEqual(data["temperature"], 25.5)
        self.assertEqual(data["humidity"], 60.0)

    async def test_garbage_handling(self):
        """Test that garbage bytes before SYNC are discarded."""
        garbage = b'\x00\xFF\xAA\xBB'
        protocol = DemeterProtocolV2()
        # Ping frame
        frame = protocol.create_ping(target_id=1)
        
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
