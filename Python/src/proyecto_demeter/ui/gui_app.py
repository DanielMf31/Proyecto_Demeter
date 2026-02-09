import customtkinter as ctk
import asyncio
import threading
import json
import socket
import logging
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from proyecto_demeter.shared.schemas import GpioCommand, ActionResponse
except ImportError:
     # Fallback
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from src.proyecto_demeter.shared.schemas import GpioCommand, ActionResponse

# Configuración Visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class DemeterGuiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍌 Demeter V2 Control Panel")
        self.geometry("600x400")
        
        # Grid Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Demeter V2", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="🔴 Desconectado", text_color="red")
        self.status_label.grid(row=1, column=0, padx=20, pady=10)

        # --- Main Area ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.label_ctrl = ctk.CTkLabel(self.main_frame, text="Control GPIO", font=("Arial", 18))
        self.label_ctrl.pack(pady=10)

        self.btn_on = ctk.CTkButton(self.main_frame, text="ENCENDER PIN 2", command=lambda: self.send_gpio_cmd(2, "ON"))
        self.btn_on.pack(pady=10)
        
        self.btn_off = ctk.CTkButton(self.main_frame, text="APAGAR PIN 2", command=lambda: self.send_gpio_cmd(2, "OFF"), fg_color="red")
        self.btn_off.pack(pady=10)
        
        self.btn_toggle = ctk.CTkButton(self.main_frame, text="TOGGLE PIN 2", command=lambda: self.send_gpio_cmd(2, "TOGGLE"), fg_color="orange")
        self.btn_toggle.pack(pady=10)

        self.log_box = ctk.CTkTextbox(self.main_frame, height=150)
        self.log_box.pack(pady=20, padx=20, fill="x")
        
        # --- Asyncio Setup ---
        self.loop = asyncio.new_event_loop()
        self.writer = None
        self.reader = None
        self.connected = False
        
        self.network_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.network_thread.start()

    def start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_service())
        self.loop.run_forever()

    async def connect_to_service(self):
        while not self.connected:
            try:
                self.update_log("Intentando conectar a 127.0.0.1:8888...")
                self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
                self.connected = True
                self.update_status(True)
                self.update_log("✅ Conectado al Servicio Demeter")
            except Exception as e:
                self.update_log(f"❌ Fallo conexión: {e}. Reintentando en 3s...")
                await asyncio.sleep(3)

    def send_gpio_cmd(self, pin, action):
        if self.connected and self.loop.is_running():
            cmd = GpioCommand(pin=pin, action=action)
            asyncio.run_coroutine_threadsafe(self._async_send(cmd), self.loop)
        else:
            self.update_log("⚠️ No conectado al servicio.")

    async def _async_send(self, cmd: GpioCommand):
        try:
            # Serializar con Pydantic
            json_str = cmd.model_dump_json()
            self.writer.write(json_str.encode())
            await self.writer.drain()
            self.update_log(f"📤 TX: {cmd.action} PIN {cmd.pin}")
            
            # Leer respuesta
            data = await self.reader.read(1024)
            if data:
                resp_json = data.decode()
                try:
                    resp = ActionResponse.model_validate_json(resp_json)
                    icon = "🟢" if resp.status == "OK" else "🔴"
                    self.update_log(f"📥 {icon} RX: {resp.message}")
                except Exception:
                    self.update_log(f"📥 RX (Raw): {resp_json}")

        except Exception as e:
            self.update_log(f"❌ Error TX: {e}")
            self.connected = False
            self.update_status(False)
            asyncio.create_task(self.connect_to_service())

    def update_log(self, text):
        self.after(0, lambda: self._append_log(text))

    def _append_log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        
    def update_status(self, connected):
        color = "green" if connected else "red"
        text = "🟢 Conectado" if connected else "🔴 Desconectado"
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

if __name__ == "__main__":
    app = DemeterGuiApp()
    app.mainloop()
