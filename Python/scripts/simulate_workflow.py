import sys
import os
import time
import logging
import threading
from unittest.mock import MagicMock

# Add Root to Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.device_manager import DeviceManager
from src.core.protocol_v2 import DemeterProtocolV2, CMD_SET_GPIO
from src.transport.uart_gateway import UartGateway

# Setup Logging
log_file = os.path.join(os.path.dirname(__file__), '..', 'logs', 'simulation_demo.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] [%(levelname)s] > %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout) # Also print to console
    ]
)

logger = logging.getLogger("SIMULATION")

class MockSerial:
    """Simulates the Physical UART connection."""
    def __init__(self):
        self.is_open = True
        self.in_waiting = 0
        self.rx_buffer = b''
        
    def write(self, data):
        logger.info(f"[PHY TX] Transmitting Bytes to Cable: {data.hex(' ').upper()}")
        # Here we could simulate a response delay
        threading.Timer(0.1, lambda: self._sim_ack(data)).start()
        
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
            # ACK Frame: SYNC(1) LEN(0) FLAGS(0) SRC(Gateway) DST(Master) CMD_ACK(2) CRC
            # FE 00 00 01 00 02 CRC
            ack_frame = b'\xFE\x00\x00\x01\x00\x02\x03' # Dummy CRC
            
            logger.info(f"[PHY RX] Hardware Sent ACK: {ack_frame.hex(' ').upper()}")
            
            self.rx_buffer += ack_frame
            self.in_waiting = len(self.rx_buffer)

    def close(self):
        pass

def run_simulation():
    logger.info("=== INICIANDO SIMULACIÓN DE FLUJO REAL (DEMETER V2) ===")
    
    # 1. Initialize Components
    logger.info("[STEP 1] Inicializando Kernels...")
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'inventory.json')
    dev_mgr = DeviceManager(config_path)
    protocol = DemeterProtocolV2()
    
    # 2. Setup Mock Transport
    logger.info("[STEP 2] Levantando Gateway Transport (Mock Serial)...")
    gateway = UartGateway(port="MOCK_PORT", protocol_engine=protocol)
    
    # Inject Mock Serial
    mock_phy = MockSerial()
    gateway.serial_conn = mock_phy
    gateway.connect = lambda: True # Bypass connect
    gateway.serial_conn.is_open = True
    
    # Capture callbacks
    def on_gui_update(msg):
        logger.info(f"[GUI EVENT] Gateway notificó: {msg}")
        
    gateway.set_callback(on_gui_update)
    gateway.start()
    
    time.sleep(1) # Wait for thread init
    
    # 3. Simulate User Action: "Sequential Irrigation"
    logger.info("=== [INTERACCIÓN DE USUARIO] ===")
    logger.info("Usuario pulsa botón: 'Ejecutar Riego Secuencial'")
    
    # Logic from MainWindow
    pump_info = dev_mgr.get_target_info("bomba_riego_norte")
    fan_info = dev_mgr.get_target_info("ventilador_invernadero")
    
    if not pump_info or not fan_info:
        logger.error("Error: Dispositivos no encontrados en JSON")
        return

    pump_id = pump_info[0]
    fan_id = fan_info[0]
    
    logger.info(f"[LOGIC] Mapeando Dispositivos -> Bomba ID:{pump_id}, Fan ID:{fan_id}")
    
    steps = [
        {'target': pump_id, 'cmd': 0x10, 'pin': 4, 'val': 1, 'delay': 2000}, # Bomba ON 2s
        {'target': pump_id, 'cmd': 0x10, 'pin': 4, 'val': 0, 'delay': 500},  # Bomba OFF 0.5s
        {'target': fan_id,  'cmd': 0x10, 'pin': 12, 'val': 1, 'delay': 2000},# Fan ON 2s
        {'target': fan_id,  'cmd': 0x10, 'pin': 12, 'val': 0, 'delay': 0}    # Fan OFF
    ]
    
    logger.info(f"[LOGIC] Generando Secuencia de {len(steps)} pasos...")
    
    # 4. Generate Protocol Bytes
    frame = protocol.create_sequence(steps)
    logger.info(f"[PROTOCOL] Trama Binaria Generada ({len(frame)} bytes): {frame.hex(' ').upper()}")
    
    # 5. Send to Transport
    logger.info("[UI -> TRANSPORT] Enviando trama a la cola de salida...")
    gateway.send_frame(frame)
    
    time.sleep(2) # Wait for simulation async
    
    logger.info("=== SIMULACIÓN COMPLETADA ===")
    logger.info(f"Log guardado en: {log_file}")
    
    gateway.stop()
    gateway.join()

if __name__ == "__main__":
    run_simulation()
