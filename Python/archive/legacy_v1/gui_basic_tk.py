import tkinter as tk
import threading
import asyncio
import json
import socket
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from proyecto_demeter.shared.schemas import GpioCommand
except ImportError:
    pass # Fallback

class BasicTkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Demeter Basic (Tkinter)")
        self.geometry("400x300")
        
        self.status = tk.Label(self, text="Disconnected (Basic Tk)", fg="red")
        self.status.pack(pady=10)
        
        self.btn_on = tk.Button(self, text="ON", command=lambda: self.send("ON"))
        self.btn_on.pack(pady=5)
        
        self.btn_off = tk.Button(self, text="OFF", command=lambda: self.send("OFF"))
        self.btn_off.pack(pady=5)
        
        self.log = tk.Text(self, height=10)
        self.log.pack(pady=10)

        # Network
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()
        self.writer = None

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        self.loop.run_forever()

    async def connect(self):
        try:
            _, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
            self.after(0, lambda: self.status.config(text="Connected", fg="green"))
        except:
             self.after(0, lambda: self.status.config(text="Connection Failed", fg="red"))

    def send(self, action):
        if self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.async_send(action), self.loop)

    async def async_send(self, action):
        if self.writer:
            cmd = {"type": "GPIO_CMD", "pin": 2, "action": action}
            self.writer.write(json.dumps(cmd).encode())
            await self.writer.drain()
            self.after(0, lambda: self.log.insert(tk.END, f"Sent: {action}\n"))

if __name__ == "__main__":
    app = BasicTkApp()
    app.mainloop()
