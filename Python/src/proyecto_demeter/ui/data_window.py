import tkinter as tk
from tkinter import ttk
import logging

class DataWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Visualización de Datos")
        self.geometry("400x300")
        self.logger = logging.getLogger("DataWindow")
        
        # Style
        style = ttk.Style()
        style.configure("BigLabel.TLabel", font=("Helvetica", 24, "bold"))
        style.configure("UnitLabel.TLabel", font=("Helvetica", 12))
        style.configure("DataCard.TFrame", background="#f0f0f0", relief="raised")
        
        self._setup_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        ttk.Label(main_frame, text="Sensores Remotos", font=("Helvetica", 16)).pack(pady=(0, 20))
        
        # Node Status
        self.status_var = tk.StringVar(value="Esperando datos...")
        ttk.Label(main_frame, textvariable=self.status_var, foreground="gray").pack()
        
        # Data Container
        data_frame = ttk.Frame(main_frame)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Temperature
        temp_frame = ttk.Frame(data_frame, style="DataCard.TFrame", padding="15")
        temp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(temp_frame, text="Temperatura", font=("Helvetica", 10)).pack()
        self.temp_var = tk.StringVar(value="--.-")
        ttk.Label(temp_frame, textvariable=self.temp_var, style="BigLabel.TLabel", foreground="#e74c3c").pack()
        ttk.Label(temp_frame, text="°C", style="UnitLabel.TLabel").pack()
        
        # Humidity
        hum_frame = ttk.Frame(data_frame, style="DataCard.TFrame", padding="15")
        hum_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        ttk.Label(hum_frame, text="Humedad", font=("Helvetica", 10)).pack()
        self.hum_var = tk.StringVar(value="--.-")
        ttk.Label(hum_frame, textvariable=self.hum_var, style="BigLabel.TLabel", foreground="#3498db").pack()
        ttk.Label(hum_frame, text="%", style="UnitLabel.TLabel").pack()

    def update_data(self, node_id, temp, hum):
        self.status_var.set(f"Datos recibidos del Nodo {node_id}")
        self.temp_var.set(f"{temp:.1f}")
        self.hum_var.set(f"{hum:.1f}")
        
    def _on_close(self):
        self.destroy()
