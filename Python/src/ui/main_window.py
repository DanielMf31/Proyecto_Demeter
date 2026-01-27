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
        
        self.title("Demeter Control System V2")
        self.geometry("600x400")
        
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
        for name, info in devices.items():
            if info["type"] == "GATEWAY": continue
            
            # Frame por dispositivo
            f = ttk.Frame(dev_frame, borderwidth=1, relief="solid")
            f.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            ttk.Label(f, text=name, font=("Arial", 10, "bold")).pack(pady=2)
            ttk.Label(f, text=f"Node: {info['node_id']}").pack()
            
            # Botones Accion
            btn_on = ttk.Button(f, text="ON", command=lambda n=info['node_id'], p=info['pin']: self.send_gpio(n, p, 1))
            btn_on.pack(side=tk.LEFT, padx=2)
            
            btn_off = ttk.Button(f, text="OFF", command=lambda n=info['node_id'], p=info['pin']: self.send_gpio(n, p, 0))
            btn_off.pack(side=tk.RIGHT, padx=2)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

        # 3. Sequence Test
        seq_frame = ttk.LabelFrame(self, text="Secuencias Avanzadas")
        seq_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(seq_frame, text="Ejecutar Riego Secuencial (Zonas)", command=self.send_test_sequence).pack(fill=tk.X)

    def _bind_events(self):
        self.gateway.set_callback(self.on_message_received)

    def connect_gateway(self):
        if self.gateway.connect():
            self.lbl_status.config(text="Gateway: CONNECTED", foreground="green")
            self.gateway.start()
            
            # Sync Routes
            self.sync_routes()
        else:
            messagebox.showerror("Error", "No se pudo conectar al Gateway")

    def sync_routes(self):
        self.logger.info("Syncing routes to Gateway...")
        routes = self.dev_mgr.get_all_routes()
        for node_id, mac_bytes in routes:
            frame = self.protocol.create_route_add(node_id, mac_bytes)
            self.gateway.send_frame(frame)
        self.logger.info("Routes sent.")

    def send_gpio(self, node, pin, val):
        frame = self.protocol.create_set_gpio(node, pin, val)
        self.gateway.send_frame(frame)

    def send_test_sequence(self):
        # Demo: Turn on Pump 1 (ID 10) for 5s, then Fan (ID 11) for 2s
        steps = [
            {'target': 10, 'cmd': CMD_SET_GPIO, 'pin': 4, 'val': 1, 'delay': 5000}, # Bomba ON, wait 5s
            {'target': 10, 'cmd': CMD_SET_GPIO, 'pin': 4, 'val': 0, 'delay': 100},  # Bomba OFF
            {'target': 11, 'cmd': CMD_SET_GPIO, 'pin': 12, 'val': 1, 'delay': 2000},# Fan ON, wait 2s
            {'target': 11, 'cmd': CMD_SET_GPIO, 'pin': 12, 'val': 0, 'delay': 0}    # Fan OFF
        ]
        
        frame = self.protocol.create_sequence(steps)
        self.gateway.send_frame(frame)
        messagebox.showinfo("Secuencia", "Secuencia enviada al Gateway")

    def on_message_received(self, msg):
        # Callback from thread, careful with UI updates (use after or queue in prod)
        print(f"GUI Received: {msg}")
