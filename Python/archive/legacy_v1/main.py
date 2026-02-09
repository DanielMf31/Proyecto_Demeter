import sys
import os
import argparse
import logging
import tkinter as tk
from tkinter import messagebox
import time

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

    # 6. Setup Thread-Safe Queue
    import queue
    rx_queue = queue.Queue()

    # 7. Setup RX Callback (Puts data into Queue)
    def on_rx_data(data):
        rx_queue.put(data)
    
    transport.set_callback(on_rx_data)

    # 8. Define Queue Processor (Runs in Main Thread)
    def process_queue():
        try:
            while not rx_queue.empty():
                data = rx_queue.get_nowait()
                try:
                    # Parse Frame
                    cmd = protocol.parse_frame(data)
                    
                    if cmd and app: # Ensure App is initialized
                        from proyecto_demeter.config.schemas import DataReport
                        if isinstance(cmd, DataReport):
                            app.handle_data_report(cmd)
                        else:
                            app.log(f"RX <- {cmd}")
                    elif app:
                        # Log raw hex if parsing failed (or incomplete frame)
                        # app.log(f"RX (Raw) <- {data.hex(' ').upper()}")
                        pass
                except Exception as e:
                     if app: app.log_error(f"RX Parse Error: {e}")
        except queue.Empty:
            pass
        finally:
            # Schedule next check (50ms)
            root.after(50, process_queue)

    # Start Queue Loop
    root.after(100, process_queue)

    def on_login_success():
        nonlocal app
        logger.info("Login Successful. Showing Main Window.")
        root.deiconify() # Show main window
        
        # Initialize Main App
        app = MainWindow(root, transport, protocol)
        
        # --- Device Manager & Route Sync ---
        try:
            from proyecto_demeter.core.device_manager import DeviceManager
            from proyecto_demeter.config.schemas import RouteAdd
            
            logger.info("Loading Device Manager...")
            dm = DeviceManager()
            routes = dm.get_all_routes()
            
            if routes:
                logger.info(f"Syncing {len(routes)} routes to Gateway...")
                # user requested to comment out sync_routes for now
                pass 
            else:
                logger.info("No routes to sync.")
                
        except Exception as e:
            logger.error(f"Failed to sync routes: {e}")

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
