import sys
import os
import logging

# Add python/src to path so we can import proyecto_demeter package
# Assuming we run from the project root (where this main.py is)
sys.path.append(os.path.join(os.path.dirname(__file__), 'python', 'src'))

from proyecto_demeter.config.settings import Settings
from proyecto_demeter.protocols.device_manager import DeviceManager
from proyecto_demeter.protocols.uart_gateway import UartGateway
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2

def main():
    print("--> Iniciando Proyecto_Demeter V2 (Protocol Engine)...")
    
    try:
        # 1. Load Settings (Env/Defaults)
        settings = Settings()
        
        # Configure logging based on settings
        logging.basicConfig(level=settings.log_level)
        logger = logging.getLogger("Main")
        
        logger.info(f"Config loaded. App: {settings.app_name}")
        
        # 2. Initialize Device Manager (Loads inventory.json)
        # We assume inventory.json is in python/config/inventory.json
        # DeviceManager logic (updated) handles the resolution relative to itself.
        dev_mgr = DeviceManager()
        
        logger.info(f"Device Manager initialized. Routes available: {len(dev_mgr.get_all_routes())}")
        
        # 3. Initialize Transport
        protocol = DemeterProtocolV2()
        gateway = UartGateway(
            port=dev_mgr.get_config("serial_port"),
            baud_rate=dev_mgr.get_config("baud_rate"),
            protocol_engine=protocol
        )
        
        logger.info(f"Gateway initialized on port {gateway.port}")
        
        # 4. (Optional) Loop or UI
        # For now, just exit cleanly or keep running if we had a loop
        # input("Press Enter to Exit...") 
        
    except Exception as e:
        print(f"!!! Error crítico al iniciar: {e}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
