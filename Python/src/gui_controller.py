
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from uart_service import UARTService
import time
import os
import json
from pathlib import Path

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger('GUIController')

class DemeterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Panel - Proyecto Demeter")
        self.root.geometry("600x400")
        
        # Cargar configuración UART
        self.port = '/dev/ttyS0' # Default RPi
        self.baud = 115200
        self.load_config()
        
        # Servicio UART
        self.uart = UARTService(port=self.port, baudrate=self.baud)
        self.connected = False
        
        # Interfaz Gráfica
        self.create_widgets()
        
        # Intentar conectar al inicio
        self.connect_uart()

    def load_config(self):
        config_path = Path(__file__).parent.parent / "config" / "settings.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.port = config.get('uart', {}).get('port', self.port)
                    self.baud = config.get('uart', {}).get('baudrate', self.baud)
            except Exception as e:
                logger.error(f"Error cargando config: {e}")

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#333", pady=10)
        header_frame.pack(fill=tk.X)
        
        lbl_title = tk.Label(header_frame, text="PROYECTO DEMETER", font=("Arial", 16, "bold"), fg="white", bg="#333")
        lbl_title.pack()
        
        # Status Bar
        self.lbl_status = tk.Label(self.root, text="Estado: Desconectado", fg="red", font=("Arial", 10))
        self.lbl_status.pack(pady=5)
        
        # Botones Frame
        buttons_frame = tk.Frame(self.root, pady=20)
        buttons_frame.pack()
        
        # Crear 5 botones
        for i in range(1, 6):
            btn = tk.Button(buttons_frame, text=f"ACTIVAR ACTUADOR {i}", 
                            command=lambda x=i: self.send_command(x),
                            font=("Arial", 12), bg="#008CBA", fg="white",
                            width=20, height=2)
            btn.pack(pady=5)
            
        # Log Area
        self.txt_log = tk.Text(self.root, height=8, width=60, state='disabled', bg="#f0f0f0")
        self.txt_log.pack(pady=10)

    def log_msg(self, msg):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def connect_uart(self):
        if self.uart.connect():
            self.connected = True
            self.lbl_status.config(text=f"Conectado a {self.port} @ {self.baud}", fg="green")
            self.log_msg("Conexión serial establecida.")
        else:
            self.connected = False
            self.lbl_status.config(text="Error de Conexión", fg="red")
            self.log_msg("No se pudo conectar al puerto serial.")
            messagebox.showerror("Error", f"No se pudo abrir el puerto {self.port}")

    def send_command(self, actuator_id):
        if not self.connected:
            messagebox.showwarning("Aviso", "No hay conexión serial")
            return

        # Formato Simple (Modo Ejecución Directa):
        # Enviaremos un código especial '200' seguido del comando, O simplemente el comando si el ESP lo soporta.
        # Basado en el plan, vamos a enviar el paquete estándar: "1 X 0 1000 0"
        # Pero modificaremos el ESP32 para que si recibe esto, lo ejecute.
        
        # Comando: Opcode=200, Tipo=1, Actuador=ID, Param=0, Duracion=1000ms, Rsv=0
        cmd_str = f"200 1 {actuator_id} 0 1000 0"
        
        self.uart.send(cmd_str)
        self.log_msg(f"-> Enviado: {cmd_str}")
        
        # Leer respuesta (breve polling)
        self.root.after(100, self.check_response)

    def check_response(self):
        if not self.connected: return
        
        response = self.uart.receive()
        if response:
            self.log_msg(f"<- Recibido: {response}")
            if "104" in response: # Si el ESP responde OK
                self.log_msg("   [OK] Ejecución confirmada")

if __name__ == "__main__":
    root = tk.Tk()
    app = DemeterGUI(root)
    root.mainloop()
