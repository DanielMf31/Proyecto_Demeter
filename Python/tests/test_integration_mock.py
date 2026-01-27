import unittest
import sys
import os
import time
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.transport.uart_gateway import UartGateway
from src.core.protocol_v2 import DemeterProtocolV2

class TestIntegrationMock(unittest.TestCase):
    """
    Simulates the full flow: App -> Gateway -> (Mock Serial) -> Gateway -> App
    """

    @patch('serial.Serial')
    def test_send_flow(self, mock_serial_cls):
        # 1. Setup Mock Serial
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_instance.in_waiting = 0 # No incoming data initially
        mock_serial_cls.return_value = mock_serial_instance

        # 2. Init Gateway
        gateway = UartGateway(port="mock_port")
        connected = gateway.connect()
        self.assertTrue(connected)
        
        # Start Thread
        gateway.start()

        # 3. Simulate UI Action (Send Data)
        test_frame = b'\xFE\x01\x02\x03' # Dummy frame
        gateway.send_frame(test_frame)
        
        # Wait a bit for thread to process
        time.sleep(0.1)
        
        # 4. Verify Serial.write was called
        mock_serial_instance.write.assert_called_with(test_frame)
        
        # 5. Stop
        gateway.stop()
        gateway.join(timeout=1)

    @patch('serial.Serial')
    def test_receive_flow(self, mock_serial_cls):
        # 1. Setup Mock for Rx
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        
        # Simulate incoming valid frame: Ping (Sync + Len=0 + Flags=0 + Src=0 + Dst=0 + Cmd=1 + CRC)
        # CRC(0+0+0+0+1) = 1
        rx_bytes = b'\xFE\x00\x00\x00\x00\x01\x01'
        
        # Generator to simulate data arriving
        mock_serial_instance.in_waiting = len(rx_bytes)
        mock_serial_instance.read.return_value = rx_bytes
        
        mock_serial_cls.return_value = mock_serial_instance

        # 2. Setup Gateway with Callback
        gateway = UartGateway(port="mock_port")
        gateway.connect()
        
        received_msgs = []
        def on_msg(msg):
            received_msgs.append(msg)
        
        gateway.set_callback(on_msg)
        gateway.start()
        
        # Wait for thread loop to read
        time.sleep(0.2)
        
        # 3. Verify
        self.assertTrue(len(received_msgs) > 0, "Callback should have been triggered")
        msg = received_msgs[0]
        self.assertEqual(msg['cmd'], 1) # Command ID 1 (Ping)
        
        gateway.stop()
        gateway.join()

if __name__ == '__main__':
    unittest.main()
