
import serial
import time
import logging

class UARTService:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_connection = None
        self.logger = logging.getLogger('UARTService')
        
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
        """Envía un mensaje string terminándolo con salto de línea (compatible con println)"""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Asegurar que termina en newline
                if not message.endswith('\n'):
                    message += '\n'
                
                self.serial_connection.write(message.encode('utf-8'))
                # Pequeña pausa para estabilidad, similar al delay(2) de C++
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
                    line = self.serial_connection.readline()
                    decoded_line = line.decode('utf-8').strip()
                    if decoded_line:
                        return decoded_line
            except Exception as e:
                self.logger.error(f"Error al recibir datos: {e}")
        return None

    def clear_buffer(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
