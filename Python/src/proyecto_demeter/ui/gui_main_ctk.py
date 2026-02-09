import customtkinter as ctk
import asyncio
import threading
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from proyecto_demeter.ui.views import SidebarFrame, ControlPanelFrame, LogConsoleFrame, SequencePlannerFrame
from proyecto_demeter.ui.viewmodel import DemeterViewModel
from proyecto_demeter.shared.schemas import SequenceStep

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class DemeterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Demeter V2 - Professional Dashboard")
        self.geometry("1000x700")

        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Views ---
        self.sidebar = SidebarFrame(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=0, sticky="nsew")
        
        self.tab_ctrl = self.tabview.add("Control")
        self.tab_plan = self.tabview.add("Planner")
        self.tab_mon = self.tabview.add("Monitor")
        
        # Configure Tab Grids
        self.tab_ctrl.grid_columnconfigure(0, weight=1)
        self.tab_ctrl.grid_rowconfigure(0, weight=1)
        
        self.tab_plan.grid_columnconfigure(0, weight=1)
        self.tab_plan.grid_rowconfigure(0, weight=1)

        self.tab_mon.grid_columnconfigure(0, weight=1)
        self.tab_mon.grid_rowconfigure(0, weight=1)

        # Log Console (Shared: small log in Control, big one in Monitor)
        # Using a single console instance for simplicity, placed in Monitor for now
        self.console = LogConsoleFrame(self.tab_mon)
        self.console.grid(row=0, column=0, sticky="nsew")

        # --- ViewModel & Async ---
        self.loop = asyncio.new_event_loop()
        
        # Callback Bridges
        # We use .after() to ensure thread safety when VM calls back from Async Thread
        self.vm = DemeterViewModel(
            self.loop,
            log_callback=lambda msg: self.after(0, self.console.append_log, msg),
            status_callback=lambda connected: self.after(0, self.sidebar.update_status, connected)
        )
        
        # Control Panel (Injects VM command)
        self.controls = ControlPanelFrame(
            self.tab_ctrl, 
            command_callback=self.trigger_command
        )
        self.controls.pack(fill="both", expand=True)

        # Sequence Planner
        self.planner = SequencePlannerFrame(self.tab_plan)
        self.planner.pack(fill="both", expand=True)

        # Start Background Thread
        self.network_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.network_thread.start()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.vm.connect())
        self.loop.run_forever()

    def trigger_command(self, pin, action):
        """Bridge UI button -> Async VM"""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.vm.send_command(pin, action), self.loop)

    def trigger_ping(self, target_id):
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.vm.send_ping(target_id), self.loop)

    def trigger_sequence_payload(self, steps_data: list):
        """
        Takes list of dicts from Planner UI, converts to Schema, and sends.
        steps_data: [{"pin": 2, "value": 1, "delay_ms": 1000}, ...]
        """
        try:
            steps = []
            for s in steps_data:
                steps.append(SequenceStep(
                    target_id=s.get("target_id", 1),
                    pin=s["pin"],
                    value=s["value"],
                    delay_ms=s["delay_ms"]
                ))
            
            if self.loop.is_running():
                asyncio.run_coroutine_threadsafe(self.vm.send_sequence(steps), self.loop)
        except Exception as e:
            self.console.append_log(f"Error building sequence: {e}")

    def on_closing(self):
        self.vm.shutdown()
        self.quit() # Stop mainloop
        # self.loop.stop() # Ideally stop loop gracefully

if __name__ == "__main__":
    app = DemeterApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
