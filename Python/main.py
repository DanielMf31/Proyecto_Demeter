import sys
import os
import argparse
import logging
import tkinter as tk
from tkinter import messagebox

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from proyecto_demeter.transport.uart import UartTransport
from proyecto_demeter.transport.mock import MockTransport
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.ui.main_window import MainWindow

# Configure Logging
import datetime

# Ensure logs directory
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Generate Session Filename
session_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_file = os.path.join(log_dir, f"session_{session_id}.log")

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("Main")
logger.info(f"=== Session Started: {session_id} ===")
logger.info(f"Logging to: {log_file}")

def main():
    # 1. Parse Arguments
    parser = argparse.ArgumentParser(description="Demeter Control Application")
    parser.add_argument("port", nargs="?", default=None, help="Serial Port (e.g. /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud Rate (Default: 115200)")
    parser.add_argument("--mock", action="store_true", help="Run in Simulation Mode (No Hardware)")
    args = parser.parse_args()

    # 2. Setup Transport
    transport = None
    if args.mock:
        logger.info("Starting in MOCK Mode")
        transport = MockTransport()
    else:
        # Determine Port
        port = args.port or os.environ.get("DEMETER_PORT", "/dev/ttyUSB0")
        logger.info(f"Starting in UART Mode on {port} @ {args.baud}")
        transport = UartTransport(port=port, baud_rate=args.baud)

    # 3. Setup Protocol
    protocol = DemeterProtocolV2()

    # 4. Connect Transport
    if not transport.connect():
        logger.error("Failed to connect transport.")
        # If not mock, we might want to show error but allow GUI to open? 
        # For now, let's allow opening but warn.
        # But UartTransport.start() might fail if not connected.
        # Let's try to start anyway or handle it in UI?
        # Standard UartTransport usually needs serialization.
        # MainWindow expects a connected transport strictly speaking?
        # Let's just warn.
    else:
        transport.start()

    # 5. Launch GUI
    root = tk.Tk()
    root.withdraw() # Hide main window initially

    # App placeholder
    app = None

    def on_login_success():
        nonlocal app
        logger.info("Login Successful. Showing Main Window.")
        root.deiconify() # Show main window
        
        # Initialize Main App
        app = MainWindow(root, transport, protocol)
        
        # Wire up RX Callback
        def on_rx_data(data):
            try:
                # 1. Parse Frame
                cmd = protocol.parse_frame(data)
                
                if cmd:
                    from proyecto_demeter.config.schemas import DataReport
                    if isinstance(cmd, DataReport):
                        # Dispatch to App
                        root.after(0, lambda: app.handle_data_report(cmd))
                    else:
                        # Log generic commands
                        root.after(0, lambda: app.log(f"RX <- {cmd}"))
                else:
                    # Log raw hex if parsing failed (or incomplete frame)
                    root.after(0, lambda: app.log(f"RX (Raw) <- {data.hex(' ').upper()}"))
            except Exception as e:
                 root.after(0, lambda: app.log_error(f"RX Parse Error: {e}"))
        
        transport.set_callback(on_rx_data)

        # --- Device Manager & Route Sync ---
        try:
            from proyecto_demeter.core.device_manager import DeviceManager
            from proyecto_demeter.config.schemas import RouteAdd
            
            logger.info("Loading Device Manager...")
            dm = DeviceManager() # Loads config/devices.json by default
            routes = dm.get_all_routes()
            
            if routes:
                logger.info(f"Syncing {len(routes)} routes to Gateway...")
                # Note: We need a delay or wait for transport to be ready
                # Small delay to ensure boot
                root.after(2000, lambda: sync_routes(routes, transport, protocol, app)) 
            else:
                logger.info("No routes to sync.")
                
        except Exception as e:
            logger.error(f"Failed to sync routes: {e}")

    def sync_routes(routes, transport, protocol, app):
        from proyecto_demeter.config.schemas import RouteAdd
        for node_id, mac_bytes in routes:
             # RouteAdd requires: target_id, node_id_to_register, mac_address_bytes
             # mac_bytes is already bytes (from DeviceManager)
             cmd = RouteAdd(target_id=1, node_id_to_register=node_id, mac_address_bytes=mac_bytes)
             frame = protocol.serialize(cmd)
             if transport:
                 transport.send(frame)
                 app.log(f"Synced Route Node {node_id}")
                 time.sleep(0.1)

    from proyecto_demeter.ui.login_window import LoginWindow
    login = LoginWindow(root, on_login_success)

    # Handle Close
    def on_close():
        logger.info("Shutting down...")
        transport.stop()
        transport.disconnect()
        root.destroy()
        sys.exit(0)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
