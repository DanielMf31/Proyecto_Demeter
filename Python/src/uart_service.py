
import serial
import time
import logging

class UARTService:
    def __init__(self, port='/dev/serial0', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        # Usamos un logger hijo del sistema principal
        self.logger = logging.getLogger('Demeter.UART')
        
    def connect(self):
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.logger.info(f"Conectado exitosamente a {self.port} a {self.baudrate} baudios.")
            return True
        except serial.SerialException as e:
            self.logger.error(f"Error al conectar con {self.port}: {e}")
            return False

    def close(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            self.logger.info("Conexión serial cerrada.")

    def send(self, message):
        """Envía un mensaje string terminándolo con salto de línea"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Asegurar que termina en newline
                if not message.endswith('\n'):
                    message += '\n'
                
                # Log de traza (DEBUG)
                raw_bytes = message.encode('utf-8')
                self.logger.debug(f"TX >> {raw_bytes.hex().upper()} | '{message.strip()}'")
                
                self.serial_connection.write(raw_bytes)
                time.sleep(0.002) 
                return True
            except Exception as e:
                self.logger.error(f"Error al enviar datos: {e}")
                return False
        return False

    def receive(self):
        """Lee una línea completa del puerto serial"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting > 0:
                    raw_data = self.serial_connection.readline()
                    
                    if raw_data:
                        # Log de traza (DEBUG)
                        self.logger.debug(f"RX << {raw_data.hex().upper()}")
                        
                        try:
                           decoded_line = raw_data.decode('utf-8').strip()
                           if decoded_line:
                               return decoded_line
                        except UnicodeDecodeError:
                            self.logger.warning(f"Bytes no decodificables recibidos: {raw_data.hex()}")
                            return None
            except Exception as e:
                self.logger.error(f"Error al recibir datos: {e}")
        return None

    def clear_buffer(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
