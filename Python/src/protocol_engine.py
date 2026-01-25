
import time
import logging

# Constantes del Protocolo (Copiadas de ProtocoloComunicacion.h)
CODIGO_SOLICITUD_CONEXION = 101
CODIGO_CONFIRMACION_CONEXION = 102
CODIGO_DATOS_RECIBIDOS = 103
CODIGO_VERIFICACION_CORRECTA = 104
CODIGO_ERROR_VERIFICACION = 105

# Estados
ESTADO_INICIAL = 0
ESPERANDO_CONFIRMACION_102 = 1
TRANSMITIENDO_DATOS = 2
ESPERANDO_103_Y_DATOS = 3
VERIFICANDO_DATOS = 4
COMUNICACION_COMPLETADA = 5
ERROR_COMUNICACION = 6
ERROR_TIMEOUT = 7

class ProtocolEngine:
    def __init__(self, uart_service):
        self.uart = uart_service
        self.logger = logging.getLogger('ProtocolEngine')
        
        self.state = ESTADO_INICIAL
        self.data_to_transmit = [] # Lista de 5 listas [5 enteros]
        self.data_received_echo = [] # Lista de listas recibidas para verificar
        
        self.timeout_start = 0
        self.TIMEOUT_MS = 10000 # 10 segundos
        self.got_103 = False

    def configure_data(self, data):
        """Configura los 5 comandos a enviar (lista de 5 listas de 5 enteros)"""
        if len(data) != 5:
            self.logger.error("Debe proporcionar exactamente 5 comandos.")
            return False
        self.data_to_transmit = data
        return True

    def start_protocol(self):
        self.reset()
        self.uart.clear_buffer()
        
        self.logger.info("Iniciando Handshake (Enviando 101)...")
        self.uart.send(f"{CODIGO_SOLICITUD_CONEXION}")
        
        self.state = ESPERANDO_CONFIRMACION_102
        self.timeout_start = time.time() * 1000

    def reset(self):
        self.state = ESTADO_INICIAL
        self.data_received_echo = []
        self.got_103 = False
        self.timeout_start = 0

    def get_state_text(self):
        states = {
            0: "INICIAL", 1: "ESPERANDO_102", 2: "TRANSMITIENDO",
            3: "ESPERANDO_103", 4: "VERIFICANDO", 5: "COMPLETADA",
            6: "ERROR_COM", 7: "ERROR_TIMEOUT"
        }
        return states.get(self.state, "DESCONOCIDO")

    def _transmit_data(self):
        self.logger.info("Transmitiendo 5 paquetes de datos...")
        for i, cmd in enumerate(self.data_to_transmit):
            # Formato: "1 1 0 1000 0"
            msg = " ".join(map(str, cmd))
            self.uart.send(msg)
            self.logger.info(f"  -> Enviado [{i}]: {msg}")
            time.sleep(0.05) # Pequeño delay entre envíos
            
        self.logger.info("Datos enviados. Esperando código 103 (Eco)...")

    def _verify_data(self):
        if len(self.data_received_echo) != 5:
            self.logger.error("Cantidad incorrecta de datos de eco.")
            return

        is_correct = True
        for i in range(5):
            sent = self.data_to_transmit[i]
            received = self.data_received_echo[i]
            
            if sent != received:
                self.logger.error(f"Mismatch en comando {i}: Enviado {sent} != Recibido {received}")
                is_correct = False
                break
        
        if is_correct:
            self.logger.info("✅ Verificación CORRECTA. Enviando 104.")
            self.uart.send(f"{CODIGO_VERIFICACION_CORRECTA}")
            self.state = COMUNICACION_COMPLETADA
        else:
            self.logger.error("❌ Verificación FALLIDA. Enviando 105.")
            self.uart.send(f"{CODIGO_ERROR_VERIFICACION}")
            self.state = ERROR_COMUNICACION

    def process(self):
        # 1. Leer mensajes
        while True:
            msg = self.uart.receive()
            if not msg:
                break
            
            # Intentar parsear el código o datos
            parts = msg.split()
            if not parts:
                continue
                
            try:
                first_val = int(parts[0])
            except ValueError:
                self.logger.warning(f"Mensaje ignorado (no numérico): {msg}")
                continue

            # Lógica de estados
            if first_val == CODIGO_CONFIRMACION_CONEXION:
                if self.state == ESPERANDO_CONFIRMACION_102:
                    self.logger.info("Recibido 102 (ACK). Iniciando transmisión...")
                    self.state = TRANSMITIENDO_DATOS
                    self._transmit_data()
                    # Pasamos a esperar 103 inmediatamente después de transmitir
                    self.state = ESPERANDO_103_Y_DATOS # En C++ esto se hace al recibir el 103, pero aquí esperamos
                    self.got_103 = False
                    self.timeout_start = time.time() * 1000

            elif first_val == CODIGO_DATOS_RECIBIDOS:
                if self.state == ESPERANDO_103_Y_DATOS or self.state == TRANSMITIENDO_DATOS:
                    self.logger.info("Recibido 103 (Inicio de Eco). Esperando datos...")
                    self.got_103 = True
                    self.data_received_echo = []
            
            elif len(parts) == 5:
                # Asumimos que es un paquete de datos de eco
                if self.got_103:
                    try:
                        cmd_echo = [int(x) for x in parts]
                        self.data_received_echo.append(cmd_echo)
                        self.logger.info(f"  <- Eco recibido: {cmd_echo}")
                        
                        if len(self.data_received_echo) == 5:
                            self.state = VERIFICANDO_DATOS
                            self._verify_data()
                    except ValueError:
                        self.logger.error(f"Error parseando datos de eco: {msg}")

        # 2. Verificar Timeouts
        if self.state not in [ESTADO_INICIAL, COMUNICACION_COMPLETADA, ERROR_COMUNICACION, ERROR_TIMEOUT]:
             current_time = time.time() * 1000
             if (current_time - self.timeout_start) > self.TIMEOUT_MS:
                 self.logger.error("TIMEOUT: No se recibió respuesta del receptor.")
                 self.state = ERROR_TIMEOUT
