import tkinter as tk
from tkinter import ttk
import logging
from ..protocols.protocol_v2 import DemeterProtocolV2
from ..protocols import CmdId, SetGpio
from ..transport.interface import TransportStrategy

class MainWindow:
    def __init__(self, root: tk.Tk, transport: TransportStrategy, protocol: DemeterProtocolV2):
        self.root = root
        self.transport = transport
        self.protocol = protocol
        self.logger = logging.getLogger("UI")
        
        self.root.title("Demeter Control V2")
        self.root.geometry("400x300")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame for Controls
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Control Manual ESP32 (Target ID: 1)", font=("Helvetica", 12, "bold")).pack(pady=10)
        
        # Grid for Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        # GPIOs to control: 4, 5, 6, 7
        self.create_gpio_control(btn_frame, 4, 0, 0)
        self.create_gpio_control(btn_frame, 5, 1, 0)
        self.create_gpio_control(btn_frame, 6, 0, 1)
        self.create_gpio_control(btn_frame, 7, 1, 1)

        # Log Area
        self.log_text = tk.Text(main_frame, height=8, width=40, state='disabled')
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

    def create_gpio_control(self, parent, pin, row, col):
        frame = ttk.LabelFrame(parent, text=f"GPIO {pin}")
        frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        ttk.Button(frame, text="ON", command=lambda: self.send_gpio(pin, 1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="OFF", command=lambda: self.send_gpio(pin, 0)).pack(side=tk.LEFT, padx=2)

    def send_gpio(self, pin, val):
        # Create Command (Target ID 1 = ESP32/Gateway usually)
        cmd = SetGpio(target_id=1, pin=pin, value=val)
        
        # Serialize
        frame = self.protocol.serialize(cmd)
        
        # Send
        if self.transport.send(frame):
            self.log(f"TX: GPIO {pin} -> {val} ({frame.hex()})")
        else:
            self.log(f"ERROR: Failed to send GPIO {pin}")

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.logger.info(msg)
