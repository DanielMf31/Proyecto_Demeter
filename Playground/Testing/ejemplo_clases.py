import time

class SensorTemperatura:
    """Clase que simula un sensor de hardware real."""
    def leer_hardware(self):
        # Imaginemos que esto se conecta a un GPIO real
        print("\n[Hardware] Leyendo sensor físico (Lento)...")
        time.sleep(1) # Simula lentitud del hardware
        return 25.0   # Valor por defecto

class SistemaRiego:
    """Clase que toma decisiones basada en el sensor."""
    def __init__(self, sensor):
        self.sensor = sensor
    
    def decidir_riego(self, umbral_temp):
        # Dependencia: Llama al método del sensor
        temperatura_actual = self.sensor.leer_hardware()
        
        if temperatura_actual > umbral_temp:
            return "ACTIVAR_RIEGO"
        return "MODO_AHORRO"
