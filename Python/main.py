import sys
import os
import logging

# Add python/src to path so we can import proyecto_demeter package
# Assuming we run from the project root (where this main.py is)
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from proyecto_demeter.config.settings import Settings
from proyecto_demeter.protocols.device_manager import DeviceManager
from proyecto_demeter.transport.uart import UartTransport
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
        # protocol = DemeterProtocolV2() # Transport handles callback, protocol parses bytes
        # In this architecture, Transport just moves bytes. Protocol Logic is usually above it.
        # But UartGateway took protocol_engine. Let's see UartTransport.
        # UartTransport doesn't take protocol_engine in __init__. It has set_callback.
        
        protocol = DemeterProtocolV2()
        transport = UartTransport(
            port=dev_mgr.get_config("serial_port"),
            baud_rate=dev_mgr.get_config("baud_rate")
        )
        
        # Wire Protocol Parser to Transport RX
        # transport.set_callback(protocol.parse_frame) # This might needs an adapter since parse_frame returns obj
        
        # Actually protocol.parse_frame takes bytes and returns object. 
        # We need a handler that does something with that object.
        def on_frame_received(data):
            # 1. Parse
             cmd = protocol.parse_frame(data)
             if cmd:
                 logger.info(f"Received Command: {cmd}")

        transport.set_callback(on_frame_received)
        
        
        # 4. Launch UI
        import tkinter as tk
        from proyecto_demeter.ui import MainWindow
        
        root = tk.Tk()
        app = MainWindow(root, transport, protocol)
        
        logger.info("Starting UI Loop...")
        root.mainloop()

        # Stop transport on exit
        transport.stop()
        
    except Exception as e:
        print(f"!!! Error crítico al iniciar: {e}")
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
