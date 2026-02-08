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
    
    # Callback for RX
    # We need a way to pass data to UI. 
    # MainWindow doesn't seem to have a public 'on_data' method in the snippet I saw?
    # I need to check MainWindow again or add a method to it.
    # The snippet showed 'self.log' but not an external data handler hook clearly exposed 
    # other than passing it to transport?
    # Wait, 'mvp_gui.py' had 'on_rx_data'.
    # MainWindow logic:
    # It initializes, but who handles RX?
    
    app = MainWindow(root, transport, protocol)
    
    # Wire up RX Callback
    # MainWindow needs a method to receive data.
    # Let's assume we can add 'handle_rx' to MainWindow or use a lambda.
    # For now, I'll define a closure here using app.
    
    def on_rx_data(data):
        # Schedule GUI update on main thread
        root.after(0, lambda: app.log(f"RX <- {data.hex(' ').upper()}"))

    transport.set_callback(on_rx_data)

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
