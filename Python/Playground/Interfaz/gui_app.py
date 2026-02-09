import customtkinter as ctk
import asyncio
import threading
import json
import socket

# Configuración Visual
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AsyncGuiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🍌 Nano Banana Control Panel")
        self.geometry("400x300")
        
        # --- UI Layout ---
        self.label = ctk.CTkLabel(self, text="Panel de Control Asíncrono", font=("Arial", 20))
        self.label.pack(pady=20)
        
        self.btn_on = ctk.CTkButton(self, text="ENCENDER LED", command=lambda: self.send_command("ON"), fg_color="green")
        self.btn_on.pack(pady=10)
        
        self.btn_off = ctk.CTkButton(self, text="APAGAR LED", command=lambda: self.send_command("OFF"), fg_color="red")
        self.btn_off.pack(pady=10)
        
        self.log_box = ctk.CTkTextbox(self, height=100)
        self.log_box.pack(pady=20, padx=20, fill="x")
        self.log_area_log("Esperando conexión...")

        # --- Asyncio Setup ---
        self.loop = asyncio.new_event_loop()
        self.writer = None
        self.reader = None
        
        # Iniciar el hilo de red
        self.network_thread = threading.Thread(target=self.start_async_loop, daemon=True)
        self.network_thread.start()

    def start_async_loop(self):
        """Ejecuta el loop de asyncio en un hilo separado."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_to_server())
        self.loop.run_forever()

    async def connect_to_server(self):
        """Intenta conectar al servidor (GUI Server)."""
        try:
            self.update_log("Conectando a 127.0.0.1:8080...")
            self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8080)
            self.update_log("✅ ¡Conectado al Servidor!")
        except Exception as e:
            self.update_log(f"❌ Error de conexión: {e}")

    def send_command(self, action):
        """Llama a la función asíncrona desde el hilo de la GUI."""
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._async_send(action), self.loop)
        else:
            self.update_log("⚠️ El loop no está corriendo.")

    async def _async_send(self, action):
        """Envía el comando por TCP."""
        if not self.writer:
            self.update_log("⚠️ No conectado.")
            await self.connect_to_server()
            if not self.writer: return

        try:
            msg = {"action": action}
            data = json.dumps(msg).encode()
            self.writer.write(data)
            await self.writer.drain()
            self.update_log(f"📤 Enviado: {action}")
            
            # Leer respuesta
            response_data = await self.reader.read(1024)
            response_msg = response_data.decode()
            self.update_log(f"📥 Respuesta: {response_msg}")
            
        except Exception as e:
            self.update_log(f"❌ Error al enviar: {e}")
            self.writer = None # Forzar reconexión

    def update_log(self, text):
        """Actualiza la GUI desde cualquier hilo de forma segura."""
        self.after(0, self.log_area_log, text)

    def log_area_log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

if __name__ == "__main__":
    app = AsyncGuiApp()
    app.mainloop()
