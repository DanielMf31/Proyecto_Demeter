import customtkinter as ctk
import asyncio
import threading
import json
import socket
import logging
import os
import sys



from proyecto_demeter.shared.config.schemas import GpioCommand, ActionResponse, DataReport

# Configuración Visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class DemeterGuiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍌 Demeter V2 Control Panel")
        self.geometry("800x600")
        
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
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # --- Section: General GPIO ---
        self.lbl_gpio = ctk.CTkLabel(self.main_frame, text="Control General (GPIO)", font=("Arial", 16, "bold"))
        self.lbl_gpio.pack(pady=10, anchor="w")
        
        self.gpio_frame = ctk.CTkFrame(self.main_frame)
        self.gpio_frame.pack(fill="x", pady=5)

        self.btn_on = ctk.CTkButton(self.gpio_frame, text="ENCENDER PIN 2", command=lambda: self.send_gpio_cmd(2, "ON"))
        self.btn_on.pack(side="left", padx=10, pady=10)
        
        self.btn_off = ctk.CTkButton(self.gpio_frame, text="APAGAR PIN 2", command=lambda: self.send_gpio_cmd(2, "OFF"), fg_color="red")
        self.btn_off.pack(side="left", padx=10, pady=10)

        # --- Section: Actuator Window (Node 3) ---
        self.lbl_actuator = ctk.CTkLabel(self.main_frame, text="Actuador Ventana (Node 3)", font=("Arial", 16, "bold"))
        self.lbl_actuator.pack(pady=(20, 5), anchor="w")

        self.window_frame = ctk.CTkFrame(self.main_frame)
        self.window_frame.pack(fill="x", pady=5)

        # Status Indicators
        self.lbl_window_state = ctk.CTkLabel(self.window_frame, text="Estado: DESCONOCIDO", font=("Arial", 14))
        self.lbl_window_state.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.lbl_battery = ctk.CTkLabel(self.window_frame, text="Batería: -- V", font=("Arial", 14))
        self.lbl_battery.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        # Controls
        self.btn_open = ctk.CTkButton(self.window_frame, text="ABRIR (ON)", fg_color="green", 
                                      command=lambda: self.send_gpio_cmd(2, "ON")) 
        
        self.btn_close = ctk.CTkButton(self.window_frame, text="CERRAR (OFF)", fg_color="red",
                                       command=lambda: self.send_gpio_cmd(2, "OFF"))
        self.btn_open.grid(row=1, column=0, padx=20, pady=10)
        self.btn_close.grid(row=1, column=1, padx=20, pady=10)


        # --- Logs ---
        self.log_box = ctk.CTkTextbox(self.main_frame, height=200)
        self.log_box.pack(pady=20, padx=0, fill="x")
        
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
                
                # Start Listener
                self.loop.create_task(self.read_loop())
                
            except Exception as e:
                self.update_log(f" Fallo conexión: {e}. Reintentando en 3s...")
                await asyncio.sleep(3)

    async def read_loop(self):
        """Continuously read lines from the service."""
        while self.connected:
            try:
                line = await self.reader.readline()
                if not line:
                    self.update_log("🔌 Conexión cerrada por el servidor.")
                    self.connected = False
                    self.update_status(False)
                    break
                
                line_str = line.decode().strip()
                if not line_str: continue

                # Parse JSON
                try:
                    data = json.loads(line_str)
                    
                    # 1. ActionResponse (ACK from GUI CMD)
                    if "status" in data:
                        resp = ActionResponse.model_validate(data)
                        icon = "🟢" if resp.status == "OK" else "🔴"
                        self.update_log(f"📥 {icon} RX: {resp.message}")
                        
                        # Mock Feedback for Window (since Service returns Pin State in message sometimes)
                        if "MOCK" in resp.message and "Pin 2" in resp.message:
                             # Try to infer state from message if DataReport doesn't come
                             pass
                    
                    # 2. DataReport (Telemetry)
                    elif "temperature" in data: # Duck typing for DataReport
                        # DataReport Schema has: target_id, node_id, temperature, humidity
                        report = DataReport(**data) # Dictionary unpacking
                        
                        # Log it
                        self.update_log(f"📡 Report Node {report.node_id}: T={report.temperature} H={report.humidity}")
                        
                        # Check if Actuator (ID 3)
                        # In PRD we said: Temp=State, Hum=Battery
                    # 2. Pin Report (Actuator State)
                    elif "state" in data and "pin" in data:
                        # PIN_REPORT
                        node_id = data.get("node_id")
                        pin = data.get("pin")
                        state = data.get("state")
                        
                        if node_id == 3: # Actuator Node
                            state_str = "ABIERTO" if state else "CERRADO"
                            color = "green" if state else "red"
                            # We don't have battery here, so just update state
                            self.lbl_window_state.configure(text=f"Estado: {state_str}", text_color=color)
                            
                        self.update_log(f"💡 Pin Report Node {node_id} Pin {pin}: {state}")

                    # 3. System Report (Battery/Mode)
                    elif "battery_mv" in data:
                         # SYSTEM_REPORT
                         node_id = data.get("node_id")
                         batt_mv = data.get("battery_mv")
                         mode = data.get("mode")
                         
                         if node_id == 3:
                             volts = batt_mv / 1000.0
                             self.lbl_battery.configure(text=f"Batería: {volts:.2f} V")
                             
                         self.update_log(f"🔋 System Node {node_id} Mode={mode} Batt={batt_mv}mV")

                    # 4. DataReport / TempHumReport (Telemetry)
                    elif "temperature" in data: 
                        # TempHumReport
                        report = DataReport(**data) 
                        self.update_log(f"📡 Report Node {report.node_id}: T={report.temperature} H={report.humidity}")
                        
                        # Legacy fallback: If we still use DataReport for Actuator (not anymore), ignore it here or keep it.
                        # Since we use explicit PinReport/SystemReport now, we don't need the hack here.

                except json.JSONDecodeError:
                     self.update_log(f" JSON Error: {line_str}")
                except Exception as e:
                     self.update_log(f" Process Error: {e}")

            except Exception as e:
                self.update_log(f" Read Error: {e}")
                self.connected = False
                break
        
        # Reconnect
        if not self.connected:
             self.update_status(False)
             await self.connect_to_service()

    def update_gui_actuator(self, state, color, battery):
        self.after(0, lambda: self._update_gui_actuator_threadsafe(state, color, battery))
    
    def _update_gui_actuator_threadsafe(self, state, color, battery):
        self.lbl_window_state.configure(text=f"Estado: {state}", text_color=color)
        self.lbl_battery.configure(text=f"Batería: {battery:.2f} V")

    def send_gpio_cmd(self, pin, action):
        if self.connected and self.loop.is_running():
            cmd = GpioCommand(pin=pin, action=action)
            asyncio.run_coroutine_threadsafe(self._async_send(cmd), self.loop)
        else:
            self.update_log(" No conectado al servicio.")

    async def _async_send(self, cmd: GpioCommand):
        try:
            # Serializar con Pydantic
            msg = {"type": "GPIO_CMD", **cmd.model_dump()}
            json_str = json.dumps(msg)
            
            self.writer.write(json_str.encode() + b'\n') # Newline!
            await self.writer.drain()
            self.update_log(f" TX: {cmd.action} PIN {cmd.pin}")
            # Listeners will pick up response
            
        except Exception as e:
            self.update_log(f" Error TX: {e}")
            self.connected = False
            self.update_status(False)

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
