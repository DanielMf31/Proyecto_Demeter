import tkinter as tk
from tkinter import ttk, messagebox
import logging
from src.core.protocol_v2 import CMD_SET_GPIO

class MainWindow(tk.Tk):
    def __init__(self, device_manager, gateway, protocol):
        super().__init__()
        self.dev_mgr = device_manager
        self.gateway = gateway
        self.protocol = protocol
        self.logger = logging.getLogger("MainWindow")
        
        # Load Config Values
        title = self.dev_mgr.get_config("ui_title")
        geometry = self.dev_mgr.get_config("ui_geometry")
        
        self.title(title)
        self.geometry(geometry)
        
        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        # 1. Connection Status Bar
        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.lbl_status = ttk.Label(status_frame, text="Gateway: Disconnected", foreground="red")
        self.lbl_status.pack(side=tk.LEFT)
        
        btn_connect = ttk.Button(status_frame, text="Connect Gateway", command=self.connect_gateway)
        btn_connect.pack(side=tk.RIGHT)

        # 2. Devices Grid
        dev_frame = ttk.LabelFrame(self, text="Dispositivos Registrados")
        dev_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Iterar inventario y crear botones
        devices = self.dev_mgr.devices
        row, col = 0, 0
        
        # Only show relevant devices (Not Gateway)
        display_devices = {k:v for k,v in devices.items() if v.get("type") != "GATEWAY"}
        
        if not display_devices:
             ttk.Label(dev_frame, text="No device found in inventory.").pack()

        for name, info in display_devices.items():
            # Frame por dispositivo
            f = ttk.Frame(dev_frame, borderwidth=1, relief="solid")
            f.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Helper to safely get values
            desc = info.get("description", name)
            node_id = info["node_id"]
            pin = info["pin"]
            
            ttk.Label(f, text=desc, font=("Arial", 9, "bold")).pack(pady=2)
            ttk.Label(f, text=f"ID:{node_id} | P:{pin}").pack()
            
            # Botones Accion
            btn_on = ttk.Button(f, text="ON", width=5, command=lambda n=node_id, p=pin: self.send_gpio(n, p, 1))
            btn_on.pack(side=tk.LEFT, padx=5, pady=2)
            
            btn_off = ttk.Button(f, text="OFF", width=5, command=lambda n=node_id, p=pin: self.send_gpio(n, p, 0))
            btn_off.pack(side=tk.RIGHT, padx=5, pady=2)
            
            col += 1
            if col > 2: # 3 Columns max
                col = 0
                row += 1

        # 3. Sequence Test
        seq_frame = ttk.LabelFrame(self, text="Secuencias Avanzadas")
        seq_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(seq_frame, text="Ejecutar Riego Secuencial (Zonas)", command=self.send_test_sequence).pack(fill=tk.X, pady=5)
        
        # 4. Console Log (Optional implementation, placeholder for now)
        # log_frame = ttk.LabelFrame(self, text="System Log")
        # ...

    def _bind_events(self):
        self.gateway.set_callback(self.on_message_received)

    def connect_gateway(self):
        # Port is already configured in gateway instance
        if self.gateway.connect():
            self.lbl_status.config(text=f"Connected ({self.gateway.port})", foreground="green")
            self.gateway.start()
            
            # Sync Routes
            self.sync_routes()
        else:
            messagebox.showerror("Error", f"No se pudo conectar a {self.gateway.port}")

    def sync_routes(self):
        self.logger.info("Syncing routes to Gateway...")
        routes = self.dev_mgr.get_all_routes()
        for node_id, mac_bytes in routes:
            frame = self.protocol.create_route_add(node_id, mac_bytes)
            self.gateway.send_frame(frame)
        self.logger.info(f"Sent {len(routes)} routes to Gateway.")

    def send_gpio(self, node, pin, val):
        frame = self.protocol.create_set_gpio(node, pin, val)
        self.gateway.send_frame(frame)

    def send_test_sequence(self):
        # Demo: Turn on Pump 1 (ID 10) for 5s, then Fan (ID 11) for 2s
        # In real app, this should rely on Configured Routines, not hardcoded steps.
        # But for MVP demo this is fine.
        
        # Verify devices exist first to avoid errors
        pump = self.dev_mgr.get_target_info("bomba_riego_norte")
        fan = self.dev_mgr.get_target_info("ventilador_invernadero")
        
        if not pump or not fan:
             messagebox.showwarning("Config Error", "Device names 'bomba_riego_norte' or 'ventilador_invernadero' missing in JSON.")
             return

        steps = [
            {'target': pump[0], 'cmd': CMD_SET_GPIO, 'pin': 4, 'val': 1, 'delay': 5000},
            {'target': pump[0], 'cmd': CMD_SET_GPIO, 'pin': 4, 'val': 0, 'delay': 100},
            {'target': fan[0], 'cmd': CMD_SET_GPIO, 'pin': 12, 'val': 1, 'delay': 2000},
            {'target': fan[0], 'cmd': CMD_SET_GPIO, 'pin': 12, 'val': 0, 'delay': 0}
        ]
        
        frame = self.protocol.create_sequence(steps)
        self.gateway.send_frame(frame)
        messagebox.showinfo("Secuencia", f"Enviada secuencia de {len(steps)} pasos.")

    def on_message_received(self, msg):
        # Callback from thread
        # In a real UI, use self.after to marshal to UI thread. 
        # For simple logging print is safe-ish.
        print(f"GUI Received: {msg}")
