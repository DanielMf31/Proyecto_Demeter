import customtkinter as ctk
from typing import Callable
import json
import tkinter as tk
from tkinter import messagebox

class SidebarFrame(ctk.CTkFrame):
    def __init__(self, master, title="Demeter V2"):
        super().__init__(master, width=140, corner_radius=0)
        self.grid_rowconfigure(4, weight=1)
        
        self.logo_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.status_label = ctk.CTkLabel(self, text="DISCONNECTED", text_color="red")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Appearance Mode
        self.appearance_mode_label = ctk.CTkLabel(self, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self, values=["System", "Light", "Dark"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def update_status(self, connected: bool):
        color = "green" if connected else "red"
        text = "CONNECTED" if connected else "DISCONNECTED"
        self.status_label.configure(text=text, text_color=color)


class ControlPanelFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, command_callback: Callable[[int, int, str], None]):
        super().__init__(master)
        self.command_callback = command_callback
        
        self.label = ctk.CTkLabel(self, text="Pump Control System", font=("Arial", 18, "bold"))
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
        
        # Pump Controls (GPIO 4, 5, 6, 7)
        # 4 Pumps
        for i, pin in enumerate([4, 5, 6, 7]):
            self.create_pump_card(i+1, pin, row=i+1)

        # Actuator Window (Node 3)
        self.create_actuator_card(row=5)

    def create_actuator_card(self, row: int):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, padx=10, pady=20, sticky="ew")
        
        lbl = ctk.CTkLabel(frame, text="Window Actuator (Node 3)", font=("Arial", 16, "bold"))
        lbl.pack(pady=5)

        # Status
        self.lbl_window_state = ctk.CTkLabel(frame, text="State: UNKNOWN", text_color="gray")
        self.lbl_window_state.pack(pady=2)
        
        self.lbl_battery = ctk.CTkLabel(frame, text="Battery: -- V", text_color="gray")
        self.lbl_battery.pack(pady=2)
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        # Window Controls (Node 3)
        self.btn_open = ctk.CTkButton(btn_frame, text="OPEN", fg_color="green", 
                                      command=lambda: self.command_callback(3, 26, "ON")) 
        self.btn_open.pack(side="left", padx=10)
        
        self.btn_close = ctk.CTkButton(btn_frame, text="CLOSE", fg_color="red", 
                                       command=lambda: self.command_callback(3, 26, "OFF"))
        self.btn_close.pack(side="left", padx=10)

    def update_actuator_state(self, state_val, battery_val):
        state_str = "OPEN" if state_val > 0.5 else "CLOSED"
        color = "green" if state_val > 0.5 else "red"
        self.lbl_window_state.configure(text=f"State: {state_str}", text_color=color)
        self.lbl_battery.configure(text=f"Battery: {battery_val:.2f} V")

        # Advanced/Diagnostics
        self.lbl_advanced = ctk.CTkLabel(self, text="Diagnostics & Tools", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_advanced.grid(row=6, column=0, columnspan=2, pady=(20, 10))

        # Ping Buttons
        self.btn_ping_gw = ctk.CTkButton(self, text="PING Gateway (1)", command=lambda: self.on_ping(1))
        self.btn_ping_gw.grid(row=7, column=0, padx=5, pady=5)
        
        self.btn_ping_n2 = ctk.CTkButton(self, text="PING Node 2", command=lambda: self.on_ping(2))
        self.btn_ping_n2.grid(row=7, column=1, padx=5, pady=5)

        self.btn_ping_n3 = ctk.CTkButton(self, text="PING Node 3", command=lambda: self.on_ping(3))
        self.btn_ping_n3.grid(row=8, column=0, padx=5, pady=5)

        self.btn_get_data = ctk.CTkButton(self, text="GET REPORT (Node 2)", fg_color="purple", command=self.on_get_data)
        self.btn_get_data.grid(row=8, column=1, padx=5, pady=5)

    def on_ping(self, target_id):
        if hasattr(self.master.master.master, 'trigger_ping'):
             self.master.master.master.trigger_ping(target_id)

    def on_get_data(self):
        if hasattr(self.master.master.master, 'trigger_get_sensors'):
             self.master.master.master.trigger_get_sensors(2) # Target Node 2

    def create_pump_card(self, index: int, pin: int, row: int):
        frame = ctk.CTkFrame(self)
        frame.grid(row=row, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        
        lbl = ctk.CTkLabel(frame, text=f"Pump {index} (GPIO {pin} @ Node 3)", width=150, anchor="w")
        lbl.pack(side="left", padx=10)
        
        # Pumps are on Node 3
        btn_on = ctk.CTkButton(frame, text="START", width=80, fg_color="green", 
                               command=lambda: self.command_callback(1, pin, "ON"))
        btn_on.pack(side="right", padx=5, pady=5)
        
        btn_off = ctk.CTkButton(frame, text="STOP", width=80, fg_color="red", 
                                command=lambda: self.command_callback(1, pin, "OFF"))
        btn_off.pack(side="right", padx=5, pady=5)
        return frame


class SequencePlannerFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.steps = [] # List of dicts or objects
        
        # Layout: Left (Editor), Right (List)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Editor Frame ---
        self.editor_frame = ctk.CTkFrame(self)
        self.editor_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.editor_frame, text="Sequence Editor", font=("Arial", 16, "bold")).pack(pady=10)
        
        # Inputs
        self.input_frame = ctk.CTkFrame(self.editor_frame)
        self.input_frame.pack(pady=5, padx=5, fill="x")
        
        ctk.CTkLabel(self.input_frame, text="Pin:").grid(row=0, column=0, padx=5)
        self.entry_pin = ctk.CTkEntry(self.input_frame, width=60)
        self.entry_pin.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(self.input_frame, text="Action:").grid(row=0, column=2, padx=5)
        self.opt_action = ctk.CTkOptionMenu(self.input_frame, values=["ON", "OFF"], width=80)
        self.opt_action.grid(row=0, column=3, padx=5)

        ctk.CTkLabel(self.input_frame, text="Delay (ms):").grid(row=1, column=0, padx=5, pady=5)
        self.entry_delay = ctk.CTkEntry(self.input_frame, width=80)
        self.entry_delay.grid(row=1, column=1, columnspan=3, padx=5, pady=5)
        
        self.btn_add = ctk.CTkButton(self.editor_frame, text="Add Step", command=self.add_step)
        self.btn_add.pack(pady=10)
        
        self.btn_clear = ctk.CTkButton(self.editor_frame, text="Clear All", fg_color="gray", command=self.clear_steps)
        self.btn_clear.pack(pady=5)

        # File Operations
        ctk.CTkLabel(self.editor_frame, text="File Operations", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        self.entry_filename = ctk.CTkEntry(self.editor_frame, placeholder_text="sequence_name.json")
        self.entry_filename.pack(pady=5)
        
        self.btn_save = ctk.CTkButton(self.editor_frame, text="Save Sequence", command=self.save_sequence)
        self.btn_save.pack(pady=5)
        
        self.btn_load = ctk.CTkButton(self.editor_frame, text="Load Sequence", command=self.load_sequence)
        self.btn_load.pack(pady=5)
        
        self.btn_run = ctk.CTkButton(self.editor_frame, text="RUN RELOADED", fg_color="orange", command=self.run_sequence)
        self.btn_run.pack(pady=20)

        # --- List Frame ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.list_frame, text="Steps Preview", font=("Arial", 16, "bold")).pack(pady=10)
        self.textbox = ctk.CTkTextbox(self.list_frame)
        self.textbox.pack(fill="both", expand=True, padx=5, pady=5)
        
    def add_step(self):
        try:
            pin = int(self.entry_pin.get())
            action = self.opt_action.get()
            delay = int(self.entry_delay.get())
            val = 1 if action == "ON" else 0
            
            step = {"pin": pin, "value": val, "delay_ms": delay, "target_id": 1} # Default target 1
            self.steps.append(step)
            self.refresh_preview()
        except ValueError:
            pass # Ignore invalid inputs

    def clear_steps(self):
        self.steps = []
        self.refresh_preview()

    def refresh_preview(self):
        self.textbox.delete("1.0", "end")
        for i, s in enumerate(self.steps):
            act = "ON" if s["value"] == 1 else "OFF"
            self.textbox.insert("end", f"{i+1}. GPIO {s['pin']} -> {act} ({s['delay_ms']}ms)\n")

    def save_sequence(self):
        name = self.entry_filename.get()
        if not name: return
        if not name.endswith(".json"): name += ".json"
        
        # Bridge to VM
        # self.master.master... access is ugly. 
        # Ideally we pass a callback or VM reference.
        # Check if root has vm
        # Root is ctk.CTk -> DemeterApp (in gui_main_ctk.py)
        # views -> TabView -> DemeterApp
        app = self.winfo_toplevel() 
        if hasattr(app, "vm"):
            app.vm.save_sequence_file(name, self.steps)

    def load_sequence(self):
        name = self.entry_filename.get()
        if not name: return
        if not name.endswith(".json"): name += ".json"
        
        app = self.winfo_toplevel()
        if hasattr(app, "vm"):
            loaded = app.vm.load_sequence_file(name)
            if loaded:
                self.steps = loaded
                self.refresh_preview()

    def run_sequence(self):
        app = self.winfo_toplevel()
        if hasattr(app, "trigger_sequence_payload"):
             app.trigger_sequence_payload(self.steps)


class LogConsoleFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.label = ctk.CTkLabel(self, text="System Logs", anchor="w")
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.textbox = ctk.CTkTextbox(self, width=250)
        self.textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def append_log(self, text: str):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
