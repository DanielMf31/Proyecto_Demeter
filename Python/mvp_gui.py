import sys
import os
import argparse
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time

# Ensure we can import proyecto_demeter
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from proyecto_demeter.transport.uart import UartTransport
from proyecto_demeter.transport.mock import MockTransport
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import CmdId

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MVP_GUI")

"""
Demeter MVP GUI Application.

This module provides a standalone Tkinter-based Graphical User Interface (GUI)
for controlling the ESP32 GPIO pins via UART (Serial) using the Demeter Protocol V2.

Features:
- Auto-detection of Serial Ports (or manual override via CLI args).
- Optimistic UI updates for instant feedback.
- Real-time HEX logging of transmitted and received frames.
- Direct integration with `UartTransport` and `DemeterProtocolV2`.

Usage:
    python mvp_gui.py [serial_port]
    
    Example:
        python mvp_gui.py /dev/ttyUSB0
"""

class DemeterMVPApp:
    """
    Main Application Controller for the MVP GUI.
    
    Manages the Tkinter Root Window, Transport Layer, and Protocol Logic.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Demeter Control MVP (Direct UART)")
        self.root.geometry("600x500")
        
        # --- LOGIC COMPONENTS ---
        # Initialize Protocol & Transport
        self.protocol = DemeterProtocolV2()
        
        # Parse Arguments
        parser = argparse.ArgumentParser(description="Demeter MVP GUI")
        parser.add_argument("port", nargs="?", default=None, help="Serial Port (e.g. /dev/ttyUSB0)")
        parser.add_argument("--mock", action="store_true", help="Run in Simulation Mode (No Hardware)")
        args = parser.parse_args()

        if args.mock:
            self.transport = MockTransport()
            self.root.title("Demeter Control MVP (SIMULATION MODE)")
        else:
            # Try finding port: Arg -> Env -> Default
            port = args.port if args.port else os.environ.get("DEMETER_PORT", "/dev/ttyUSB0")
            self.transport = UartTransport(port=port, baud_rate=115200)
        self.transport.set_callback(self.on_rx_data)
        
        # --- GUI COMPONENTS ---
        self.create_widgets()
        
        # --- PIN STATE TRACKING (Local Optimistic) ---
        self.pin_states = {
            4: False,
            5: False,
            6: False,
            7: False
        }
        
        # Start Transport
        if self.transport.connect():
            self.transport.start()
            self.log_msg(f"Connected to {self.transport.port}")
        else:
            self.log_msg(f"Failed to connect to {self.transport.port}")

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="Demeter GPIO Control", font=("Arial", 16, "bold"))
        header.pack(pady=10)
        
        # Buttons Frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)
        
        self.buttons = {}
        
        pins = [4, 5, 6, 7]
        for i, pin in enumerate(pins):
            # Create a Canvas based button representation or just colorable buttons
            # Tkinter ttk buttons are hard to color. Use standard tk.Button
            btn = tk.Button(btn_frame, text=f"PIN {pin}", font=("Arial", 12, "bold"),
                            width=10, height=3,
                            command=lambda p=pin: self.toggle_pin(p))
            btn.grid(row=0, column=i, padx=10)
            self.buttons[pin] = btn
            self.update_btn_color(pin, False) # Init Red

        # Log Console
        log_frame = ttk.LabelFrame(self.root, text="Serial Console")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, state='disabled', height=10)
        self.log_area.pack(fill="both", expand=True)

    def update_btn_color(self, pin, is_on):
        color = "#4CAF50" if is_on else "#F44336" # Green / Red
        self.buttons[pin].config(bg=color, activebackground=color)

    def toggle_pin(self, pin):
        # 1. Update Logic
        new_state = not self.pin_states[pin]
        self.pin_states[pin] = new_state
        
        # 2. Update UI (Optimistic)
        self.update_btn_color(pin, new_state)
        
        # 3. Send Command
        val_int = 1 if new_state else 0
        cmd_bytes = self.protocol.create_set_gpio(target_id=1, pin=pin, value=val_int)
        
        self.transport.send(cmd_bytes)
        self.log_msg(f"TX -> Set GPIO {pin} to {val_int}")

    def on_rx_data(self, data):
        # Callback from Transport Thread
        # Use root.after_idle to update UI safely if needed
        # For MVP just log bytes
        hex_str = data.hex(' ').upper()
        self.root.after(0, self.log_msg, f"RX <- {hex_str}")

    def log_msg(self, msg):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def on_close(self):
        self.transport.stop()
        self.transport.disconnect()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DemeterMVPApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
