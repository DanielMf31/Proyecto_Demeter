import logging
import sys
import os

# Configurar Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Añadir root al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.device_manager import DeviceManager
from src.core.protocol_v2 import DemeterProtocolV2
from src.transport.uart_gateway import UartGateway
from src.ui.main_window import MainWindow

def main():
    logger = logging.getLogger("Main")
    logger.info("Starting Demeter System V2 Migration...")

    # 1. Initialize Core Services
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "inventory.json")
        dev_mgr = DeviceManager(config_path)
        protocol = DemeterProtocolV2()
        
        # 2. Initialize Transport (No connect yet)
        # Assuming Gateway is on /dev/ttyACM0 (Standard for ESP32)
        gateway = UartGateway(port='/dev/ttyACM0', protocol_engine=protocol)
        
        # 3. Initialize UI
        app = MainWindow(dev_mgr, gateway, protocol)
        
        # 4. Run Loop
        app.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal Error: {e}", exc_info=True)
    finally:
        if 'gateway' in locals() and gateway:
            gateway.stop()

if __name__ == "__main__":
    main()
