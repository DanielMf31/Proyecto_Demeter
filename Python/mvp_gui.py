import sys
import os
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time

# Ensure we can import proyecto_demeter
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from proyecto_demeter.transport.uart import UartTransport
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.protocols.schemas_protocol import CmdId

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MVP_GUI")

class DemeterMVPApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Demeter Control MVP (Direct UART)")
        self.root.geometry("600x500")
        
        # --- LOGIC COMPONENTS ---
        # Initialize Protocol & Transport
        self.protocol = DemeterProtocolV2()
        
        # Try finding port: First arg, then env, then default
        port = sys.argv[1] if len(sys.argv) > 1 else '/dev/ttyUSB0' # Default for PC testing usually
        # On Raspberry Pi it might be /dev/serial0
        
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
