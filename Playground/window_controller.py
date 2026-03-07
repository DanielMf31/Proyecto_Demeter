import math
import time
from typing import Dict, List, Optional
from collections import deque

class SensorFilter:
    """Filtro Paso Bajo implementado como Media Móvil Simple (SMA).
    Mantiene una ventana de tamaño fijo (por defecto 5) y devuelve la media.
    Esto previene el 'chattering' causado por ruido momentáneo en los sensores.
    """
    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self._history: Dict[str, deque] = {}

    def update(self, key: str, value: float) -> float:
        """Añade un valor histórico para la clave y retorna la media actual."""
        if key not in self._history:
            self._history[key] = deque(maxlen=self.window_size)
        self._history[key].append(value)
        return sum(self._history[key]) / len(self._history[key])


class Thermodynamics:
    """Cálculos psicrométricos y termodinámicos según fórmulas del SDK de Demeter."""
    
    @staticmethod
    def calculate_vapor_pressure(temp_c: float) -> float:
        """Presión de vapor de saturación de Magnus-Tetens (kPa)."""
        return 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))

    @staticmethod
    def calculate_enthalpy(temp_c: float, hr: float, pressure_kpa: float = 101.325) -> float:
        """Calcula la Entalpía específica (kJ/kg) usando fórmulas ASHRAE.
        Utilizado para comparar la energía del aire exterior frente al interior.
        """
        # Presión de vapor de saturación (kPa)
        es = Thermodynamics.calculate_vapor_pressure(temp_c)
        # Presión de vapor actual (kPa)
        ea = es * (hr / 100.0)
        
        # Humedad específica / Relación de mezcla (kg agua / kg aire seco)
        r = (0.622 * ea) / (pressure_kpa - ea)
        
        # Entalpía específica (kJ/kg)
        h = 1.006 * temp_c + r * (2501 + 1.86 * temp_c)
        return h


class PIDController:
    """Controlador P-I-D en Tiempo Discreto con Anti-Windup Integral."""
    
    def __init__(self, kp: float, ki: float, kd: float, 
                 setpoint: float, out_min: float = 0.0, out_max: float = 100.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        self.setpoint = setpoint
        self.out_min = out_min
        self.out_max = out_max
        
        self._last_error = 0.0
        self._integral = 0.0
        self._last_time = None

    def calculate(self, pv: float, current_time: Optional[float] = None) -> float:
        """Iteración del PID. pv = Process Variable (Temperatura interior)."""
        if current_time is None:
            current_time = time.time()
            
        if self._last_time is None:
            dt = 1.0  # Primera iteración, asumir dt=1 para evitar math error
        else:
            dt = current_time - self._last_time
            if dt <= 0:
                dt = 0.001

        error = self.setpoint - pv
        
        # Componente Proporcional
        p_term = self.kp * error
        
        # Componente Integral (Integración trapezoidal / euler hacia atrás)
        i_step = self.ki * error * dt
        self._integral += i_step
        
        # Componente Derivativo
        d_term = self.kd * (error - self._last_error) / dt
        
        output = p_term + self._integral + d_term
        
        # ANTI-WINDUP: Si el actuador satura, deshacemos el paso integral
        if output > self.out_max:
            if error > 0: # Evitar acumular si ya excede techo superior
                self._integral -= i_step
            output = self.out_max
            
        elif output < self.out_min:
            if error < 0: # Evitar acumular si ya excede suelo inferior
                self._integral -= i_step
            output = self.out_min

        self._last_error = error
        self._last_time = current_time
        
        return output


class GreenhouseController:
    """Cerebro Central del Invernadero. Orquestador del pipeline de control."""
    
    # Constantes Físicas y Operativas
    MAX_OPENING_DUE_TO_ENTHALPY = 10.0  # % max si exterior es muy húmedo/cálido
    SOLAR_FEEDFORWARD_THRESHOLD = 600.0 # W/m2
    DEADBAND_THRESHOLD = 10.0           # Diferencia mínima en % para actuar mecánicamente

    def __init__(self, target_temp: float = 24.0):
        # Filtros
        self.filter_t_in = None  # Lazy init
        self.filter_t_out = None
        self.filter_hr_in = None
        self.filter_hr_out = None
        self.filter_wind = None
        self.filter_solar = None
        
        # Actuador Virtual
        self.current_window_opening = 0.0  # Empieza cerrado
        
        # PID (Notar que el error es Setpoint - PV. 
        # Como queremos ABRIR ventana cuando hace calor (PV > Setpoint),
        # P debe ser NEGATIVO. (e.g., PV=30, SP=24 -> Error=-6 -> out = (-1)*(Error) = +6)
        self.pid = PIDController(kp=-5.0, ki=-0.1, kd=-0.5, setpoint=target_temp)

    def _init_filters(self, window_size: int = 5):
        if self.filter_t_in is None:
            self.filter_t_in = SensorFilter(window_size)
            self.filter_t_out = SensorFilter(window_size)
            self.filter_hr_in = SensorFilter(window_size)
            self.filter_hr_out = SensorFilter(window_size)
            self.filter_wind = SensorFilter(window_size)
            self.filter_solar = SensorFilter(window_size)

    def tick(self, inputs: Dict[str, float]) -> None:
        """
        Invocado en cada ciclo de lazo de control (e.g. 1 minuto).
        inputs dict con claves: 'temp_in', 'hr_in', 'temp_out', 'hr_out', 'wind', 'rain', 'solar'
        """
        self._init_filters()
        
        print("\n--- NUEVA LECTURA ---")
        print(f"Brutos -> T_in:{inputs['temp_in']}°C H_in:{inputs['hr_in']}% | "
              f"T_ext:{inputs['temp_out']}°C H_ext:{inputs['hr_out']}% Viento:{inputs['wind']} Lluvia:{inputs['rain']} Sol:{inputs['solar']}")
        
        # 1. FILTRADO (Media Móvil)
        t_in = self.filter_t_in.update('t_in', inputs['temp_in'])
        hr_in = self.filter_hr_in.update('hr_in', inputs['hr_in'])
        t_out = self.filter_t_out.update('t_out', inputs['temp_out'])
        hr_out = self.filter_hr_out.update('hr_out', inputs['hr_out'])
        wind = self.filter_wind.update('wind', inputs['wind'])
        solar = self.filter_solar.update('solar', inputs['solar'])
        
        print(f"Filtrados -> T_in:{t_in:.1f}°C H_in:{hr_in:.1f}% | "
              f"T_ext:{t_out:.1f}°C H_ext:{hr_out:.1f}% Viento:{wind:.1f}")

        # 2. ENCLAVAMIENTO DE SEGURIDAD ABSOLUTA
        # lluvia no se promedia, al primer indicio se cierra
        if inputs.get('rain', False) or wind > 40.0:
            print("🚨 ALERTA DE SEGURIDAD: Lluvia o Viento Extremo. Forzando Cierre.")
            self._move_window(0.0, forced=True)
            return

        # 3. TERMODINÁMICA (Decidir límite físico)
        h_in = Thermodynamics.calculate_enthalpy(t_in, hr_in)
        h_out = Thermodynamics.calculate_enthalpy(t_out, hr_out)
        
        max_limit = 100.0
        if h_out > h_in:
            # El exterior tiene más energía térmica (calor sensible + latente) que adentro.
            print(f"⚠️ Termodinámica: h_ext ({h_out:.1f}) > h_int ({h_in:.1f}). Restringiendo apertura máxima a {self.MAX_OPENING_DUE_TO_ENTHALPY}%.")
            max_limit = self.MAX_OPENING_DUE_TO_ENTHALPY
            
        self.pid.out_max = max_limit # Modificar techo del PID sobre la marcha (Anti-Windup protegerá interno)

        # 4. PID Y FEED-FORWARD
        pid_output = self.pid.calculate(pv=t_in)
        
        # Feed-Forward Solar: Anticipar calor
        if solar > self.SOLAR_FEEDFORWARD_THRESHOLD:
            print(f"☀️ Fuerte sol detectado ({solar:.0f} W/m2). Añadiendo +15% de feed-forward.")
            pid_output += 15.0  

        # Clampeo final
        pid_output = max(0.0, min(max_limit, pid_output))
        
        print(f"🧠 PID Salida calculada: {pid_output:.1f}% (Setpoint: {self.pid.setpoint}°C)")

        # 5. BANDA MUERTA
        self._move_window(pid_output)


    def _move_window(self, target_percent: float, forced: bool = False):
        """Simulador de accionamiento del motor físico."""
        target_percent = round(target_percent, 1)
        
        if forced:
            if self.current_window_opening != target_percent:
                print(f"[MOTOR] >>> Moviendo motores de ventanas de {self.current_window_opening:.1f}% a: {target_percent}% (FORZADO)")
                self.current_window_opening = target_percent
            else:
                print(f"[MOTOR] Ya están en posición segura: {target_percent}%")
            return

        delta = abs(target_percent - self.current_window_opening)
        if delta >= self.DEADBAND_THRESHOLD:
            print(f"[MOTOR] >>> Moviendo motores de ventanas de {self.current_window_opening:.1f}% a: {target_percent}% (Delta: {delta:.1f}%)")
            self.current_window_opening = target_percent
        else:
            print(f"[MOTOR] Evitando movimiento. Delta {delta:.1f}% < Banda Muerta ({self.DEADBAND_THRESHOLD}%)")


if __name__ == "__main__":
    import random
    
    # --- SIMULADOR DE DÍA ---
    print("====== INICIO DE SIMULACIÓN ======")
    controller = GreenhouseController(target_temp=24.0)
    
    # Secuencia 1: Día calmado, la temperatura interior sube lentamente, el exterior está fresco
    print("\n--- FASE 1: Subida de Temperatura Constante ---")
    for step in range(1, 6):
        inputs = {
            'temp_in': 22.0 + (step * 1.5),  # 23.5, 25.0, 26.5, 28.0, 29.5
            'hr_in': 60.0,
            'temp_out': 20.0,
            'hr_out': 50.0,
            'wind': 10.0 + random.uniform(-2, 2),
            'rain': False,
            'solar': 300.0  # Soleado pero no extremo
        }
        controller.tick(inputs)
        time.sleep(0.1) # Simulando t entre lecturas

    # Secuencia 2: Impacto del Sol directo activando el Feed-Forward
    print("\n--- FASE 2: Sol Fuerte (Feed-Forward) ---")
    for step in range(6, 8):
        inputs = {
            'temp_in': 30.0, 
            'hr_in': 58.0,
            'temp_out': 21.0,
            'hr_out': 50.0,
            'wind': 15.0,
            'rain': False,
            'solar': 800.0   # Activa feed-forward
        }
        controller.tick(inputs)
        time.sleep(0.1)

    # Secuencia 3: Tormenta imprevista. Viento > 40 y luego lluvia.
    print("\n--- FASE 3: TORMENTA HURACANADA ---")
    # Paso 8: Rafagas de viento intensas detectadas, pero no lluvia
    inputs = {
        'temp_in': 29.0, 'hr_in': 70.0,
        'temp_out': 35.0,  # El exterior se vuelve asquerosamente húmedo y caliente (para ver restricción de Entalpía si abriera)
        'hr_out': 90.0,
        'wind': 55.0,      # > 40 km/h -> Trigger de Interlock
        'rain': False,
        'solar': 100.0
    }
    controller.tick(inputs)
    time.sleep(0.1)
    
    # Paso 9-10: Tormenta descargando, viento baja pero hay lluvia
    for step in range(9, 11):
        inputs['wind'] = 30.0
        inputs['rain'] = True # -> Trigger de Interlock
        controller.tick(inputs)
        time.sleep(0.1)
        
    print("\n====== FIN DE SIMULACIÓN ======")
