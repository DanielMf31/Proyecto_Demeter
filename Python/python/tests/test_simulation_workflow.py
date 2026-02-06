import unittest
import sys
import os
import time
import logging
import threading
from unittest.mock import MagicMock

# Add Root to Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.protocols.device_manager import DeviceManager
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2, CMD_SET_GPIO
from proyecto_demeter.protocols.uart_gateway import UartGateway

# Log to a separate file for this test
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, 'test_simulation_workflow.log')

class MockSerial:
    """Simulates the Physical UART connection."""
    def __init__(self, logger):
        self.is_open = True
        self.in_waiting = 0
        self.rx_buffer = b''
        self.logger = logger
        
    def write(self, data):
        self.logger.info(f"[PHY TX] Transmitting Bytes to Cable: {data.hex(' ').upper()}")
        # Here we could simulate a response delay
        threading.Timer(0.1, lambda: self._sim_ack(data)).start()
    
    def close(self):
        pass
        
    def read(self, count):
        if not self.rx_buffer:
            return b''
        ret = self.rx_buffer[:count]
        self.rx_buffer = self.rx_buffer[count:]
        self.in_waiting = len(self.rx_buffer)
        return ret

    def _sim_ack(self, causing_frame):
        """Simulate hardware replying with ACK after processing."""
        # Simple Logic: If frame starts with FE, reply with ACK
        if causing_frame.startswith(b'\xFE'):
            # ACK Frame: SYNC(1) LEN(0) FLAGS(0) SRC(Gateway) DST(Master) 02 CRC
            # FE 00 00 01 00 02 CRC
            ack_frame = b'\xFE\x00\x00\x01\x00\x02\x03' # Dummy CRC
            
            self.logger.info(f"[PHY RX] Hardware Sent ACK: {ack_frame.hex(' ').upper()}")
            
            self.rx_buffer += ack_frame
            self.in_waiting = len(self.rx_buffer)

class TestSimulationWorkflow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Configure logging specifically for this test run
        cls.logger = logging.getLogger("TEST_SIMULATION")
        cls.logger.setLevel(logging.DEBUG)
        
        # Clear handlers to avoid duplicate logs if running in suite
        cls.logger.handlers = []
        
        file_handler = logging.FileHandler(LOG_FILE, mode='w')
        file_handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s] > %(message)s'))
        cls.logger.addHandler(file_handler)
        
        cls.logger.info("=== STARTING INTEGRATION SIMULATION TEST ===")

    def test_full_sequential_workflow(self):
        self.logger.info("[STEP 1] Initializing Kernels...")
        
        # 1. Initialize Components
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'inventory.json')
        dev_mgr = DeviceManager(config_path)
        protocol = DemeterProtocolV2()
        
        # 2. Setup Mock Transport
        self.logger.info("[STEP 2] Setting up Gateway Transport (Mock Serial)...")
        gateway = UartGateway(port="MOCK_PORT", protocol_engine=protocol)
        
        # Inject Mock Serial
        mock_phy = MockSerial(self.logger)
        gateway.serial_conn = mock_phy
        gateway.connect = lambda: True # Bypass connect
        gateway.serial_conn.is_open = True
        
        # Capture callbacks to verify response
        received_msgs = []
        def on_gui_update(msg):
            self.logger.info(f"[GUI EVENT] Gateway notified: {msg}")
            received_msgs.append(msg)
            
        gateway.set_callback(on_gui_update)
        gateway.start()
        
        time.sleep(0.5) # Wait for thread init
        
        # 3. Simulate User Action: "Sequential Irrigation"
        self.logger.info("=== [USER INTERACTION] ===")
        self.logger.info("User clicks: 'Execute Sequential Irrigation'")
        
        target_name_pump = "bomba_riego_norte"
        target_name_fan = "ventilador_invernadero"
        
        pump_info = dev_mgr.get_target_info(target_name_pump)
        fan_info = dev_mgr.get_target_info(target_name_fan)
        
        # Assert config is valid
        self.assertIsNotNone(pump_info, f"Device {target_name_pump} not found")
        self.assertIsNotNone(fan_info, f"Device {target_name_fan} not found")
        
        pump_id = pump_info[0]
        fan_id = fan_info[0]
        
        self.logger.info(f"[LOGIC] Devices Mapped -> Pump ID:{pump_id}, Fan ID:{fan_id}")
        
        steps = [
            {'target': pump_id, 'cmd': 0x10, 'pin': 4, 'val': 1, 'delay': 2000},
            {'target': pump_id, 'cmd': 0x10, 'pin': 4, 'val': 0, 'delay': 500},
            {'target': fan_id,  'cmd': 0x10, 'pin': 12, 'val': 1, 'delay': 2000},
            {'target': fan_id,  'cmd': 0x10, 'pin': 12, 'val': 0, 'delay': 0}
        ]
        
        self.logger.info(f"[LOGIC] Generating Sequence of {len(steps)} steps...")
        
        # 4. Generate Protocol Bytes
        frame = protocol.create_sequence(steps)
        self.logger.info(f"[PROTOCOL] Frame Generated ({len(frame)} bytes): {frame.hex(' ').upper()}")
        
        # Assert Frame Structure logic
        # Header (6) + Count(1) + 4 steps * 8 bytes + CRC(1) = 6 + 1 + 32 + 1 = 40 bytes
        self.assertEqual(len(frame), 40, "Frame size should be 40 bytes for 4 steps")
        
        # 5. Send to Transport
        self.logger.info("[UI -> TRANSPORT] Sending frame to queue...")
        gateway.send_frame(frame)
        
        # Wait for async processing
        time.sleep(1.0) 
        
        # 6. Verification
        self.logger.info("=== VERIFICATION ===")
        
        # Verify ACK received
        self.assertGreater(len(received_msgs), 0, "Should have received at least one message (ACK)")
        msg = received_msgs[0]
        
        # Check ACK content
        # ACK Cmd ID is 2
        self.assertEqual(msg['cmd'], 2, "Received message should be ACK (0x02)")
        
        self.logger.info("SUCCESS: Test Workflow Completed.")
        
        gateway.stop()
        gateway.join()

if __name__ == "__main__":
    unittest.main()
