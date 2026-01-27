import logging
import sys
import os

# Configurar logs iniciales (fijos hasta cargar config)
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

    gateway = None

    try:
        # 1. Load Configuration
        config_path = os.path.join(os.path.dirname(__file__), "config", "inventory.json")
        dev_mgr = DeviceManager(config_path)
        
        # Update Log Level from Config
        log_level_str = dev_mgr.get_config("log_level").upper()
        logging.getLogger().setLevel(log_level_str)
        logger.info(f"Log Level set to {log_level_str}")

        # 2. Initialize Core Services
        protocol = DemeterProtocolV2()
        
        # 3. Initialize Transport
        # Get Port and Baud from Config
        serial_port = dev_mgr.get_config("serial_port")
        baud_rate = dev_mgr.get_config("baud_rate")
        
        logger.info(f"Initializing Gateway on {serial_port} @ {baud_rate}")
        gateway = UartGateway(port=serial_port, baud=baud_rate, protocol_engine=protocol)
        
        # 4. Initialize UI
        app = MainWindow(dev_mgr, gateway, protocol)
        
        # 5. Run Loop
        app.mainloop()
        
    except Exception as e:
        logger.critical(f"Fatal Error: {e}", exc_info=True)
    finally:
        if gateway:
            gateway.stop()

if __name__ == "__main__":
    main()
