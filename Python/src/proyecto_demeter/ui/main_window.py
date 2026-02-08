import tkinter as tk
from tkinter import ttk
import logging
from ..protocols.protocol_v2 import DemeterProtocolV2
from ..protocols import CmdId, SetGpio
from ..transport.interface import TransportStrategy
from .sequencer_window import SequencerWindow

class MainWindow:
    """
    Tkinter Main Window for the Demeter Control App.
    
    Provides buttons to toggle GPIO pins and a log area to view traffic.
    Serves as the View layer in the MVC pattern (Model: Protocol, Controller: App/Main).
    
    Args:
        root (tk.Tk): The root Tkinter window.
        transport (TransportStrategy): Configured transport layer for sending commands.
        protocol (DemeterProtocolV2): Protocol engine for serialization.
    """
    def __init__(self, root: tk.Tk, transport: TransportStrategy, protocol: DemeterProtocolV2):
        self.root = root
        self.transport = transport
        self.protocol = protocol
        self.logger = logging.getLogger("UI")
        
        self.root.title("Demeter Control V2")
        self.root.geometry("500x400")
        
        # Apply Theme
        style = ttk.Style()
        style.theme_use('clam') # Modern-ish look
        
        # Configure Styles
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Helvetica", 10))
        style.configure("TButton", font=("Helvetica", 10, "bold"), padding=5)
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#333")
        
        self.root.configure(bg="#f0f0f0")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame for Controls
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Control Manual ESP32", style="Header.TLabel").pack(pady=(0, 20))
        
        # Grid for Buttons
        btn_frame = ttk.Labelframe(main_frame, text=" Actuadores (GPIO) ", padding=10)
        btn_frame.pack(pady=10, fill="x")
        
        # GPIOs to control: 4, 5, 6, 7
        # GPIOs to control: 4, 5, 6, 7 in a 2x2 grid
        self.create_gpio_control(btn_frame, 4, 0, 0)
        self.create_gpio_control(btn_frame, 5, 0, 1)
        self.create_gpio_control(btn_frame, 6, 1, 0)
        self.create_gpio_control(btn_frame, 7, 1, 1)

        # Sequencer Button
        ttk.Button(main_frame, text="📅 Abrir Planificador de Secuencias", command=self.open_sequencer).pack(pady=15, fill="x")

        # Log Area
        log_frame = ttk.Labelframe(main_frame, text=" Monitor Serial ", padding=5)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(log_frame, height=8, width=40, state='disabled', bg="#222", fg="#0f0", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)

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

    def open_sequencer(self):
        # Open Toplevel Window
        # Pass protocol and transport send method
        SequencerWindow(self.root, self.protocol, self.transport.send)
