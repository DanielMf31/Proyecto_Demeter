import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List
from ..protocols.schemas_sequencer import SequenceStep
from ..protocols.protocol_v2 import DemeterProtocolV2, ExecSequence, SequenceStep as ProtoStep

class SequencerWindow(tk.Toplevel):
    def __init__(self, parent, protocol: DemeterProtocolV2, send_callback: Callable[[bytes], None]):
        super().__init__(parent)
        self.title("Planificador de Secuencias")
        self.geometry("500x400")
        
        self.protocol = protocol
        self.send_callback = send_callback
        self.steps: List[SequenceStep] = []
        
        self.setup_ui()
        
    def setup_ui(self):
        # --- INPUT FRAME ---
        input_frame = ttk.Labelframe(self, text=" Nuevo Paso ", padding=10)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Pin Selector
        ttk.Label(input_frame, text="Pin GPIO:").grid(row=0, column=0, padx=5, sticky="e")
        self.combo_pin = ttk.Combobox(input_frame, values=["4", "5", "6", "7"], state="readonly", width=5)
        self.combo_pin.current(0)
        self.combo_pin.grid(row=0, column=1, padx=5, sticky="w")
        
        # Action Selector
        ttk.Label(input_frame, text="Acción:").grid(row=0, column=2, padx=5, sticky="e")
        self.combo_action = ttk.Combobox(input_frame, values=["ON", "OFF"], state="readonly", width=5)
        self.combo_action.current(0)
        self.combo_action.grid(row=0, column=3, padx=5, sticky="w")
        
        # Duration
        ttk.Label(input_frame, text="Duración (ms):").grid(row=0, column=4, padx=5, sticky="e")
        self.entry_duration = ttk.Entry(input_frame, width=8)
        self.entry_duration.insert(0, "1000")
        self.entry_duration.grid(row=0, column=5, padx=5, sticky="w")
        
        # Add Button
        ttk.Button(input_frame, text="➕ Añadir Paso", command=self.add_step).grid(row=0, column=6, padx=15)
        
        # --- LIST FRAME ---
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill="both", expand=True)
        
        cols = ("#", "Pin", "Estado", "Demora (ms)")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=8)
        
        self.tree.heading("#", text="#")
        self.tree.heading("Pin", text="Pin")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Demora (ms)", text="Demora")
        
        self.tree.column("#", width=30, anchor="center")
        self.tree.column("Pin", width=50, anchor="center")
        self.tree.column("Estado", width=80, anchor="center")
        self.tree.column("Demora (ms)", width=100, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # --- ACTION BUTTONS ---
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="🗑️ Limpiar", command=self.clear_steps).pack(side="left")
        ttk.Button(btn_frame, text="🚀 ENVIAR SECUENCIA", command=self.send_sequence).pack(side="right")
        
    def add_step(self):
        try:
            pin = int(self.combo_pin.get())
            action_str = self.combo_action.get()
            value = 1 if action_str == "ON" else 0
            duration = int(self.entry_duration.get())
            
            if duration <= 0:
                raise ValueError("La duración debe ser positiva")
            
            step = SequenceStep(pin=pin, value=value, delay_ms=duration)
            self.steps.append(step)
            
            # Update UI
            idx = len(self.steps)
            self.tree.insert("", "end", values=(idx, pin, action_str, duration))
            
        except ValueError as e:
            messagebox.showerror("Error", f"Entrada inválida: {e}")
            
    def clear_steps(self):
        self.steps.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
            
    def send_sequence(self):
        if not self.steps:
            messagebox.showwarning("Aviso", "La lista de pasos está vacía")
            return
            
        try:
            # Convert Pydantic High Level Steps to Protocol Low Level Steps
            proto_steps = []
            for s in self.steps:
                # Target ID 1 (ESP32), Cmd ID 0x10 (GPIO)
                proto_steps.append(ProtoStep(
                    target_id=1,
                    cmd_id=0x10, # CMD_SET_GPIO
                    pin=s.pin,
                    value=s.value,
                    delay_ms=s.delay_ms
                ))
            
            cmd = ExecSequence(target_id=1, steps=proto_steps)
            frame = self.protocol.serialize(cmd)
            
            self.send_callback(frame)
            messagebox.showinfo("Éxito", f"Secuencia de {len(self.steps)} pasos enviada correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error de Protocolo", str(e))
