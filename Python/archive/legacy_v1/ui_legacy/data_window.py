import tkinter as tk
from tkinter import ttk

class DataWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Monitor de Datos (Telemetry)")
        self.geometry("400x300")
        
        ttk.Label(self, text="Real-time Data", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        self.tree = ttk.Treeview(self, columns=("Node", "Temp", "Hum"), show='headings')
        self.tree.heading("Node", text="Node ID")
        self.tree.heading("Temp", text="Temp (°C)")
        self.tree.heading("Hum", text="Humidity (%)")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.items = {} # Map NodeID -> ItemID

    def update_data(self, node_id, temp, hum):
        if node_id in self.items:
            self.tree.item(self.items[node_id], values=(node_id, f"{temp:.2f}", f"{hum:.2f}"))
        else:
            item_id = self.tree.insert("", tk.END, values=(node_id, f"{temp:.2f}", f"{hum:.2f}"))
            self.items[node_id] = item_id
