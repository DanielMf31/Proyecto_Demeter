import tkinter as tk
from tkinter import ttk, messagebox
import logging
import time
from ..protocols.protocol_v2 import DemeterProtocolV2
from ..config.schemas import CmdId, SetGpio, Ping, DataReport
from ..transport.interface import TransportStrategy
from .sequencer_window import SequencerWindow
from ..core.device_manager import DeviceManager
from ..core.sensor_logger import SensorLogger

class MainWindow:
    """
    Tkinter Main Window for the Demeter Control App.
    Refactored to use Tabs (Notebook) for layout.
    
    Tab 1: Control (GPIO + Ping + Monitor)
    Tab 2: Sequencer
    """
    def __init__(self, root: tk.Tk, transport: TransportStrategy, protocol: DemeterProtocolV2):
        self.root = root
        self.transport = transport
        self.protocol = protocol
        self.logger = logging.getLogger("UI")
        self.device_manager = DeviceManager() # Load devices
        self.sensor_logger = SensorLogger()   # Init CSV Logger
        self.data_window = None               # Reference to Data Window
        
        self.root.title("Demeter Control V3 (ESP-Now)")
        self.root.geometry("800x600") # Larger for tabs
        
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        # 1. Create Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 2. Create Tabs
        self.tab_control = ttk.Frame(self.notebook)
        self.tab_sequencer = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_control, text=" 🎛️ Control & Monitor ")
        self.notebook.add(self.tab_sequencer, text=" 📅 Sequencer ")
        
        # 3. Setup Tab 1: Control
        self.setup_control_tab()
        
        # 4. Setup Tab 2: Sequencer
        # We instantiate SequencerWindow but inject the tab frame as parent
        # Note: SequencerWindow originally was Toplevel. We might need to adjust it 
        # or just extract its widgets.
        # Ideally, SequencerWindow should accept a parent frame.
        # Let's see if we can adapt it.
        self.sequencer_app = SequencerWindow(self.tab_sequencer, self.protocol, self.transport.send, is_tab=True)

    def setup_control_tab(self):
        # Frame for Controls
        main_frame = ttk.Frame(self.tab_control, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        
        ttk.Label(main_frame, text="Gateway & Node Control", font=("Helvetica", 14, "bold")).pack(pady=(0, 20))
        
        # --- Toolbar ---
        toolbar = ttk.Frame(main_frame)
        toolbar.pack(fill="x", pady=5)
        ttk.Button(toolbar, text="🔄 Sincronizar Rutas (UART)", command=self.send_sync_routes).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="📊 Monitor de Datos", command=self.open_data_window).pack(side=tk.LEFT)

        # --- GPIO Control (Gateway) ---
        gpio_frame = ttk.Labelframe(main_frame, text=" Gateway GPIOs (Local) ", padding=10)
        gpio_frame.pack(pady=5, fill="x")
        
        self.create_gpio_control(gpio_frame, 4, 0, 0)
        self.create_gpio_control(gpio_frame, 5, 0, 1)
        self.create_gpio_control(gpio_frame, 6, 1, 0)
        self.create_gpio_control(gpio_frame, 7, 1, 1)

        # --- Network Devices (Ping) ---
        net_frame = ttk.Labelframe(main_frame, text=" Network Nodes (ESP-Now) ", padding=10)
        net_frame.pack(pady=10, fill="x")
        
        # Populate from DeviceManager
        routes = self.device_manager.get_all_routes()
        if not routes:
            ttk.Label(net_frame, text="No routes found in devices.json").pack()
        else:
            for node_id, mac in routes:
                f = ttk.Frame(net_frame)
                f.pack(fill="x", pady=2)
                mac_hex = mac.hex(':').upper()
                ttk.Label(f, text=f"Node {node_id} [{mac_hex}]", width=30).pack(side=tk.LEFT)
                ttk.Button(f, text="⚡ PING", command=lambda n=node_id: self.send_ping(n)).pack(side=tk.LEFT)

        # --- Log Area ---
        log_frame = ttk.Labelframe(main_frame, text=" Monitor Serial ", padding=5)
        log_frame.pack(fill="both", expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=60, state='disabled', bg="#222", fg="#0f0", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def create_gpio_control(self, parent, pin, row, col):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=col, padx=20, pady=5)
        
        ttk.Label(frame, text=f"GPIO {pin}: ").pack(side=tk.LEFT)
        ttk.Button(frame, text="ON", width=5, command=lambda: self.send_gpio(1, pin, 1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(frame, text="OFF", width=5, command=lambda: self.send_gpio(1, pin, 0)).pack(side=tk.LEFT, padx=2)

    def send_ping(self, target_id):
        # ... existing ping logic ...
        cmd = Ping(target_id=target_id)
        frame = self.protocol.serialize(cmd)
        if self.transport.send(frame):
            self.log(f"TX -> PING Node {target_id}")
        else:
            self.log_error(f"TX Failed: PING {target_id}")

    def send_gpio(self, target, pin, val):
        cmd = SetGpio(target_id=target, pin=pin, value=val)
        frame = self.protocol.serialize(cmd)
        if self.transport.send(frame):
            self.log(f"TX -> SetGpio({target}, {pin}, {val})")
        else:
            self.log_error(f"TX Failed: GPIO {pin}")

    def send_sync_routes(self):
        """Manually User-Triggered Route Sync"""
        from ..config.schemas import RouteAdd
        routes = self.device_manager.get_all_routes()
        if not routes:
            self.log("No routes to sync.")
            return

        success_count = 0
        for node_id, mac_bytes in routes:
            cmd = RouteAdd(node_id=node_id, mac_address=mac_bytes.hex(':'))
            frame = self.protocol.serialize(cmd)
            if self.transport.send(frame):
                success_count += 1
                time.sleep(0.1) # Small delay
        
        self.log(f"Synced {success_count}/{len(routes)} routes to Gateway.")

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        self.logger.info(msg)

    def log_error(self, msg):
        self.log(f"ERROR: {msg}")

    # --- Data Visualization ---
    def open_data_window(self):
        if self.data_window is None or not self.data_window.winfo_exists():
            from .data_window import DataWindow
            self.data_window = DataWindow(self.root)
        else:
            self.data_window.lift()

    def handle_data_report(self, report):
        """Handle incoming DataReport packet"""
        # 1. Log to generic log
        self.log(f"RX <- DATA REPORT from Node {report.node_id}: {report.temperature}°C, {report.humidity}%")
        
        # 2. Log to CSV
        if self.sensor_logger:
            self.sensor_logger.log_report(report)

        # 3. Update Window if open
        if self.data_window is not None and self.data_window.winfo_exists():
            self.data_window.update_data(report.node_id, report.temperature, report.humidity)

    # No longer needed as we use Tabs
    # def open_sequencer(self): ...
