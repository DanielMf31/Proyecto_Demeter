import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional
from tkinter import ttk, messagebox, simpledialog, filedialog
from ..config.schemas import SequenceStep, SequenceFile, ExecSequence
from ..core.sequence_manager import SequenceManager
from ..protocols.protocol_v2 import DemeterProtocolV2

class SequencerWindow(ttk.Frame):
    def __init__(self, parent, protocol: DemeterProtocolV2, send_callback: Callable[[bytes], None], is_tab=False):
        super().__init__(parent)
        self.protocol = protocol
        self.send_callback = send_callback
        self.manager = SequenceManager()
        self.steps: List[SequenceStep] = []
        
        if not is_tab and isinstance(parent, tk.Tk):
            # If not a tab, we might want a Toplevel wrapper, but since we inherit Frame,
            # we rely on the parent being a container. 
            # This refactor assumes it's always used as a Frame or inside a Toplevel.
            pass

        self.pack(fill="both", expand=True) # Self-pack
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
        
        # --- LIST FRAME (DataGrid Style) ---
        list_frame = ttk.Frame(self, padding=10)
        list_frame.pack(fill="both", expand=True)
        
        # Configure Treeview Style
        style = ttk.Style()
        style.configure("Treeview", 
                        background="#ffffff",
                        foreground="black",
                        rowheight=25,
                        fieldbackground="#ffffff",
                        font=("Arial", 10))
        style.map('Treeview', background=[('selected', '#347083')])
        
        cols = ("#", "Pin", "Estado", "Demora (ms)")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=10)
        
        self.tree.heading("#", text="#")
        self.tree.heading("Pin", text="Pin GPIO")
        self.tree.heading("Estado", text="Acción")
        self.tree.heading("Demora (ms)", text="Espera (ms)")
        
        self.tree.column("#", width=40, anchor="center")
        self.tree.column("Pin", width=80, anchor="center")
        self.tree.column("Estado", width=100, anchor="center")
        self.tree.column("Demora (ms)", width=120, anchor="center")
        
        # Tags for striped rows
        self.tree.tag_configure('odd', background='#E8E8E8')
        self.tree.tag_configure('even', background='#FFFFFF')
        
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # --- ACTION BUTTONS ---
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill="x")
        
        left_frame = ttk.Frame(btn_frame)
        left_frame.pack(side="left")
        
        ttk.Button(left_frame, text="💾 Guardar", command=self.save_sequence).pack(side="left", padx=5)
        ttk.Button(left_frame, text="📂 Cargar", command=self.load_sequence).pack(side="left", padx=5)
        ttk.Button(left_frame, text="🗑️ Limpiar", command=self.clear_steps).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="🚀 ENVIAR SECUENCIA", command=self.send_sequence).pack(side="right")
        
    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, step in enumerate(self.steps):
            action = "ON" if step.value else "OFF"
            tag = 'even' if i % 2 == 0 else 'odd'
            self.tree.insert("", "end", values=(i+1, step.pin, action, step.delay_ms), tags=(tag,))

    def save_sequence(self):
        if not self.steps:
            messagebox.showwarning("Aviso", "No hay pasos para guardar")
            return
            
        name = simpledialog.askstring("Guardar Secuencia", "Nombre de la secuencia:")
        if name:
            try:
                seq = SequenceFile(name=name, steps=self.steps)
                path = self.manager.save_sequence(name, seq)
                messagebox.showinfo("Guardado", f"Secuencia guardada en:\n{path}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_sequence(self):
        files = self.manager.list_sequences()
        if not files:
            messagebox.showinfo("Cargar", "No hay secuencias guardadas.")
            return

        # Simple Checkbox or Listbox Implementation could be complex here for Toplevel
        # For MVP, let's use FileDialog pointing to the dir
        filename = filedialog.askopenfilename(initialdir=self.manager.directory, filetypes=[("JSON Files", "*.json")])
        if filename:
            try:
                import os
                basename = os.path.basename(filename)
                seq = self.manager.load_sequence(basename)
                self.steps = seq.steps
                self.refresh_list()
                messagebox.showinfo("Cargado", f"Se cargó '{seq.name}' con {len(seq.steps)} pasos.")
            except Exception as e:
                messagebox.showerror("Error", f"Fallo al cargar: {e}")

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
            self.refresh_list()
            
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
            # Unified SequenceStep matches Protocol Step structure
            # steps are already SequenceStep objects suitable for ExecSequence
            # (they have default target_id and cmd_id)
            cmd = ExecSequence(target_id=1, steps=self.steps)
            frame = self.protocol.serialize(cmd)
            
            self.send_callback(frame)
            messagebox.showinfo("Éxito", f"Secuencia de {len(self.steps)} pasos enviada correctamente.")
            
        except Exception as e:
            messagebox.showerror("Error de Protocolo", str(e))
