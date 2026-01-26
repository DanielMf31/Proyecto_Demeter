
import tkinter as tk
from tkinter import ttk, messagebox
import logging
from uart_service import UARTService
from protocol_engine import ProtocolEngine
from config.config import config

# Logger específico para la GUI
logger = logging.getLogger('Demeter.GUI')

class DemeterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control Panel - Proyecto Demeter")
        self.root.geometry("700x500")
        
        # Configuración
        self.port = config.port
        self.baud = config.baudrate
        
        # Cola de comandos
        self.command_queue = [] # Lista de listas [tipo, id, p1, dur, p2]
        
        # Servicios
        self.uart = UARTService(port=self.port, baudrate=self.baud)
        self.protocol = ProtocolEngine(self.uart)
        self.connected = False
        
        # Interfaz Gráfica
        self.create_widgets()
        
        # Conexión Inicial
        self.connect_system()

    def log_action(self, action_name, params=None):
        """Helper para registrar acciones de usuario estandarizadas"""
        logger.info(f"ACTION: {action_name} | PARAMS: {params}")

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        header_frame.pack(fill=tk.X)
        
        lbl_title = tk.Label(header_frame, text="PROYECTO DEMETER", font=("Helvetica", 18, "bold"), fg="white", bg="#2c3e50")
        lbl_title.pack()
        
        # Status Bar
        self.lbl_status = tk.Label(self.root, text="Estado: Inicializando...", fg="gray", font=("Arial", 10))
        self.lbl_status.pack(pady=5)

        # Main Layout
        main_frame = tk.Frame(self.root, padx=20, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Columna Izquierda: Botones de Actuadores
        left_frame = tk.LabelFrame(main_frame, text="Añadir Comandos", padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for i in range(1, 6):
            btn = tk.Button(left_frame, text=f"Añadir Actuador {i}", 
                            command=lambda x=i: self.add_to_queue(x),
                            bg="#3498db", fg="white", font=("Arial", 11), width=20)
            btn.pack(pady=5)

        # Columna Derecha: Cola y Control
        right_frame = tk.LabelFrame(main_frame, text="Cola de Envío", padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.lst_queue = tk.Listbox(right_frame, height=10, width=40)
        self.lst_queue.pack(pady=5)

        btn_clear = tk.Button(right_frame, text="Limpiar Cola", command=self.clear_queue, bg="#e74c3c", fg="white")
        btn_clear.pack(fill=tk.X, pady=2)

        tk.Label(right_frame, text=" ").pack() # Spacer

        self.btn_send = tk.Button(right_frame, text="INICIAR SECUENCIA", 
                                  command=self.start_sequence, 
                                  bg="#27ae60", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_send.pack(fill=tk.X, pady=10)

        # Log Area (Visual)
        self.txt_log = tk.Text(self.root, height=8, width=80, state='disabled', bg="#ecf0f1", font=("Consolas", 9))
        self.txt_log.pack(pady=10, padx=10)

    def log_visual(self, msg):
        self.txt_log.config(state='normal')
        self.txt_log.insert(tk.END, f"> {msg}\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state='disabled')

    def connect_system(self):
        logger.info(f"Intentando conectar a {self.port}...")
        if self.uart.connect():
            self.connected = True
            logger.info("Conexión serial establecida.")
            self.lbl_status.config(text=f"Conectado: {self.port}", fg="green")
            self.log_visual("Sistema Conectado.")
        else:
            self.connected = False
            logger.error("Fallo al conectar puerto serial.")
            self.lbl_status.config(text="Error de Conexión", fg="red")
            messagebox.showerror("Error", f"No se pudo abrir {self.port}")

    def add_to_queue(self, actuator_id):
        # Limitar a 5 comandos (Protocolo actual tiene límite de 5)
        if len(self.command_queue) >= 5:
            messagebox.showwarning("Límite", "Máximo 5 comandos por secuencia.")
            return

        command = [1, actuator_id, 0, 1000, 0] # [Tipo, Act, P1, Dur(1s), P2]
        self.command_queue.append(command)
        
        self.log_action("ADD_COMMAND", {"id": actuator_id})
        self.lst_queue.insert(tk.END, f"Actuador {actuator_id} (1000ms)")
        self.log_visual(f"Añadido: Actuador {actuator_id}")

    def clear_queue(self):
        self.command_queue = []
        self.lst_queue.delete(0, tk.END)
        self.log_action("CLEAR_QUEUE")
        self.log_visual("Cola limpiada.")

    def start_sequence(self):
        if not self.connected:
            messagebox.showerror("Error", "Sin conexión")
            return
            
        if len(self.command_queue) < 1:
            messagebox.showwarning("Vacío", "Añade comandos antes de enviar.")
            return
            
        # Rrellenar hasta 5 comandos con ceros si es necesario (Protocolo espera 5)
        # O el ProtocolEngine maneja padding? ProtocolEngine espera lista de 5.
        # Vamos a hacer padding aqui para robustez
        payload = list(self.command_queue)
        while len(payload) < 5:
            payload.append([0, 0, 0, 0, 0]) # NOP
            
        self.log_action("START_SEQUENCE", {"count": len(self.command_queue)})
        self.log_visual("Iniciando transmisión de protocolo...")
        
        # Configurar Engine
        if self.protocol.configure_data(payload):
            # Ejecutar el protocolo (esto es bloqueante en TK simple, idealmente threads pero MVP OK)
            # Para MVP: Hacemos un loop simple con update de TK
            self.run_protocol_loop()
        else:
            logger.error("Error configurando datos de protocolo")

    def run_protocol_loop(self):
        """Ejecuta el protocolo paso a paso manteniendo la GUI viva"""
        self.protocol.start_protocol()
        self.btn_send.config(state='disabled', text="ENVIANDO...")
        
        def step():
            self.protocol.process()
            state = self.protocol.state
            
            # Chequear finalización
            if state == 5: # COMUNICACION_COMPLETADA
                self.log_visual("✅ SECUENCIA COMPLETADA")
                self.log_action("SEQUENCE_COMPLETE")
                messagebox.showinfo("Éxito", "Comandos enviados y verificados.")
                self.reset_ui()
                return
            
            if state in [6, 7]: # ERROR
                self.log_visual("❌ ERROR EN TRANSMISIÓN")
                logger.error(f"Fallo de protocolo. Estado: {state}")
                messagebox.showerror("Fallo", "No se completó la transmisión.")
                self.reset_ui()
                return

            # Siguiente paso en 10ms
            self.root.after(10, step)
            
        step()

    def reset_ui(self):
        self.btn_send.config(state='normal', text="INICIAR SECUENCIA")
        # Opcional: limpiar cola tras envio exitoso
        # self.clear_queue()
