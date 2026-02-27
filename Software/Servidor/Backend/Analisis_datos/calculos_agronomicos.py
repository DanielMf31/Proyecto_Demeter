import numpy as np
import pandas as pd

# --- 1. ESTADÍSTICA DESCRIPTIVA ---
def calcular_estadisticas(datos):
    """Calcula media, desviación estándar, CV y SEM."""
    if len(datos) == 0: return {}
    arr = np.array(datos)
    mu = np.mean(arr)
    sigma = np.std(arr, ddof=1) if len(arr) > 1 else 0  # Muestra
    cv = (sigma / mu) * 100 if mu != 0 else 0
    sem = sigma / np.sqrt(len(datos)) if len(datos) > 0 else 0
    return {"Media": mu, "StdDev": sigma, "CV": cv, "SEM": sem}

# --- 2. TERMODINÁMICA DEL AGUA Y AIRE ---
def calcular_presion_vapor_saturacion(T):
    """
    Calcula la presión de vapor de saturación (es) en kPa utilizando la ecuación de Tetens.
    
    :param T: Temperatura en grados Celsius (°C).
    :return: Presión de vapor de saturación en kilopascales (kPa).
    """
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))

def calcular_presion_vapor_actual(T, HR):
    """
    Calcula la presión de vapor actual (ea) en el aire en kPa.
    
    :param T: Temperatura en grados Celsius (°C).
    :param HR: Humedad Relativa en porcentaje (%).
    :return: Presión de vapor actual en kilopascales (kPa).
    """
    es = calcular_presion_vapor_saturacion(T)
    return es * (HR / 100.0)

def calcular_vpd(T, HR):
    """
    Calcula el Déficit de Presión de Vapor (VPD o DPV) en kPa.
    Indica el poder secante de la atmósfera, crucial para estimar la transpiración vegetal.
    
    :param T: Temperatura en grados Celsius (°C).
    :param HR: Humedad Relativa en porcentaje (%).
    :return: VPD en kilopascales (kPa). Será 0 si el aire está saturado.
    """
    es = calcular_presion_vapor_saturacion(T)
    ea = es * (HR / 100.0)
    return max(0, es - ea)

def calcular_punto_rocio(T, HR):
    """
    Calcula el Punto de Rocío (Dew Point), la temperatura a la cual el aire se satura.
    
    :param T: Temperatura actual en °C.
    :param HR: Humedad Relativa actual en %.
    :return: Temperatura de Punto de Rocío en °C.
    """
    ea = calcular_presion_vapor_actual(T, HR)
    if ea <= 0.0001: return -999 
    ln_val = np.log(ea / 0.6108)
    tdp = (237.3 * ln_val) / (17.27 - ln_val)
    return tdp

def calcular_humedad_absoluta(T, HR):
    """
    Calcula la masa de vapor de agua por unidad de volumen de aire.
    
    :param T: Temperatura en °C.
    :param HR: Humedad Relativa en %.
    :return: Humedad Absoluta en gramos por metro cúbico (g/m³).
    """
    ea = calcular_presion_vapor_actual(T, HR)
    tk = T + 273.15
    return (2165 * ea) / tk

def calcular_humedad_especifica(T, HR, P_kpa=101.3):
    """
    Calcula la masa de vapor de agua por masa total de aire húmedo.
    
    :param T: Temperatura en °C.
    :param HR: Humedad Relativa en %.
    :param P_kpa: Presión atmosférica en kPa (101.3 por defecto a nivel del mar).
    :return: Humedad Específica (kg/kg).
    """
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - 0.378 * ea)

def calcular_relacion_mezcla(T, HR, P_kpa=101.3):
    """
    Calcula la proporción de masa de vapor de agua por masa de aire seco.
    
    :param T: Temperatura en °C.
    :param HR: Humedad Relativa en %.
    :param P_kpa: Presión atmosférica en kPa.
    :return: Relación de mezcla r (kg/kg).
    """
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - ea)

def calcular_entalpia(T, HR, P_kpa=101.3):
    """
    Calcula el contenido total de calor del aire (Entalpía específica).
    Aproximación para aire húmedo no saturado.
    
    :param T: Temperatura en °C.
    :param HR: Humedad Relativa en %.
    :param P_kpa: Presión atmosférica normal en kPa.
    :return: Entalpía en kJ/kg de aire seco.
    """
    r = calcular_relacion_mezcla(T, HR, P_kpa)
    return 1.006 * T + r * (2501 + 1.86 * T)

def calcular_bulbo_humedo_stull(T, HR):
    """
    Calcula la Temperatura de Bulbo Húmedo usando la fórmula empírica de Stull (2011).
    Útil para medir la temperatura más baja que se puede alcanzar evaporando agua.
    
    :param T: Temperatura de bulbo seco en °C.
    :param HR: Humedad relativa en %.
    :return: Temperatura de bulbo húmedo en °C.
    """
    term1 = T * np.arctan(0.151977 * (HR + 8.313659)**0.5)
    term2 = np.arctan(T + HR)
    term3 = -np.arctan(HR - 1.676331)
    term4 = 0.00391838 * (HR**1.5) * np.arctan(0.023101 * HR)
    term5 = -4.686035
    return term1 + term2 + term3 + term4 + term5

# --- 3. FENOLOGÍA Y TIEMPO (Sin radiación) ---
def calcular_gdd(t_max, t_min, t_base=10):
    """
    Calcula los Grados Día de Crecimiento (GDD - Growing Degree Days).
    Métrica térmica que acumula el calor diario por encima de un umbral biológico.
    
    :param t_max: Temperatura máxima del día en °C.
    :param t_min: Temperatura mínima del día en °C.
    :param t_base: Temperatura base fisiológica (°C), debajo de la cual el cultivo no crece (ej: Maíz=10°C).
    :return: GDD acumulado en el día (siempre >= 0).
    """
    gdd = ((t_max + t_min) / 2) - t_base
    return max(0, gdd)

def calcular_horas_frio(temperaturas_horarias, umbral=7.2):
    """
    Calcula el modelo de Horas de Frío (Chilling Hours).
    Acumulación anual crítica para romper la latencia de frutales (ej: manzanos, cerezos).
    
    :param temperaturas_horarias: Iterable con las temperaturas de cada hora del día (°C).
    :param umbral: Temperatura máxima efectiva (°C) (0 a 7.2°C por defecto).
    :return: Cantidad de horas que caen en la ventana efectiva.
    """
    return sum(1 for t in temperaturas_horarias if 0 < t < umbral)

def calcular_chu_maiz(t_min, t_max):
    """
    Calcula el Crop Heat Units (CHU) específico para Maíz (Corn Heat Units).
    Sistema no lineal canadiense que pondera diferencialmente el calor día/noche.
    
    :param t_min: Temperatura mínima diaria (°C).
    :param t_max: Temperatura máxima diaria (°C).
    :return: Índice térmico CHU del día.
    """
    y_min = 1.8 * (t_min - 4.4)
    y_max = 3.33 * (t_max - 10) - 0.084 * (t_max - 10)**2
    return (y_max + y_min) / 2

# --- 4. ÍNDICES DE ESTRÉS Y MODELADO ---
def calcular_heat_index(T, HR):
    """
    Calcula el Índice de Calor (Sensación térmica) según la ecuación de Rothfusz (NOAA).
    
    :param T: Temperatura del aire en °C.
    :param HR: Humedad relativa en %.
    :return: Índice de calor o temperatura T aparente en °C.
    """
    if T < 27: return T 
    hi = -8.78469475556 + 1.61139411*T + 2.338548838*HR - 0.14611605*T*HR \
         - 0.012308094*T**2 - 0.0164248277*HR**2 + 0.002211732*T**2*HR \
         + 0.00072546*T*HR**2 - 0.000003582*T**2*HR**2
    return hi

def calcular_eto_hargreaves(t_min, t_max, t_media, ra_mm_dia):
    """
    Calcula la Evapotranspiración de Referencia (ETo) por la ecuación de Hargreaves-Samani.
    Especialmente útil cuando falta radiación solar o sensores de viento.
    
    :param t_min: Temperatura mínima diaria en °C.
    :param t_max: Temperatura máxima diaria en °C.
    :param t_media: Temperatura media diaria en °C.
    :param ra_mm_dia: Radiación extraterrestre en mm/día (Depende latitud/día del año).
    :return: ETo en mm/día.
    """
    return 0.0023 * ra_mm_dia * (t_media + 17.8) * np.sqrt(max(0, t_max - t_min))

def calcular_lsd(t_aire, hr):
    """
    Calcula la Diferencia de Temperatura Hoja-Aire (Leaf-To-Surrounding Difference).
    Asume simplificadamente que la hoja está unos 2°C por debajo del aire por sudoración extrema.
    
    :param t_aire: Temperatura del dosel vegetal en °C.
    :param hr: Humedad en %.
    :return: Diferencial de presión (LSD) en kPa.
    """
    t_hoja = t_aire - 2.0
    es_hoja = calcular_presion_vapor_saturacion(t_hoja)
    ea_aire = calcular_presion_vapor_actual(t_aire, hr)
    return es_hoja - ea_aire

def calcular_frost_point(t_dp):
    """
    Detecta si el punto de rocío actual implica riesgo de cristalización sobre hoja viva (Escarcha/Helada Blanca).
    
    :param t_dp: Temperatura de punto de rocío en °C.
    :return: Temperatura de formación de hielo, o None si no hay riesgo térmico (<0).
    """
    return t_dp if t_dp < 0 else None

def calcular_riesgo_wallin(horas_hr_alta, t_media):
    """
    Aproxima la severidad de Wallin (Alerta de Infección Fúngica Blight en Solanáceas).
    Se usa para evaluar enfermedades en papa o tomate basados en alta HR.
    
    :param horas_hr_alta: Horas consecutivas con Humedad Superior a 90%.
    :param t_media: Temperatura media durante ese periodo húmedo (°C).
    :return: Nivel de Riesgo (0 a 4).
    """
    if horas_hr_alta < 10: return 0
    if 10 <= t_media <= 27:
        if horas_hr_alta >= 10: return 1
        if horas_hr_alta >= 20: return 2
    return 0

def calcular_z_score(val, mu, sigma):
    """
    Calcula valor un Z-Score (desviaciones estándar respecto a la media de la serie).
    Útil para la detección de valores anómalos (Outliers OOT) en los sensores hardware (Roturas, reinicios).
    
    :param val: Valor instantáneo n.
    :param mu: Media muestral.
    :param sigma: Desviación Estándar.
    :return: Distancia en sigmas con signo.
    """
    return (val - mu) / sigma if sigma > 0 else 0

# --- PROCESADOR PRINCIPAL ---
def procesar_dataframe(df_crudo: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Motor central Analítico de Datos Agrícolas.
    Toma un DataFrame crudo con series temporales ['timestamp', 'temperature', 'humidity']
    y computa todas las métricas térmicas, hídricas y fenológicas para cada instante,
    devolviendo además un resumen agregado del periodo.
    
    :param df_crudo: DataFrame de Pandas con columnas necesarias (fechas y valores brutos).
    :return: 
        - df_horario: Dataframe con ~20 columnas calculadas hora a hora (VPD, Entalpía, Z-scores, etc).
        - df_resumen: Dataframe con estadísticas colapsadas del periodo (GDD total, ETo, Promedios).
    """
    if df_crudo.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Ordenar chronológicamente
    df_crudo = df_crudo.sort_values(by="timestamp").copy()
    
    fechas = df_crudo['timestamp'].tolist()
    temps = df_crudo['temperature'].values
    hums = df_crudo['humidity'].values
    
    # Hora artificial asumiendo 24 horas continuas
    horas = np.arange(len(df_crudo)) 

    # Estadística
    stats_t = calcular_estadisticas(temps)
    stats_h = calcular_estadisticas(hums)
    
    t_max = np.max(temps)
    t_min = np.min(temps)
    t_media = stats_t.get("Media", 0)
    
    # Derivados
    vpds = [calcular_vpd(t, h) for t, h in zip(temps, hums)]
    tdps = [calcular_punto_rocio(t, h) for t, h in zip(temps, hums)]
    has = [calcular_humedad_absoluta(t, h) for t, h in zip(temps, hums)]
    ents = [calcular_entalpia(t, h) for t, h in zip(temps, hums)]
    twbs = [calcular_bulbo_humedo_stull(t, h) for t, h in zip(temps, hums)]
    
    es_arr = [calcular_presion_vapor_saturacion(t) for t in temps]
    ea_arr = [calcular_presion_vapor_actual(t, h) for t, h in zip(temps, hums)]
    qs = [calcular_humedad_especifica(t, h) for t, h in zip(temps, hums)]
    rs = [calcular_relacion_mezcla(t, h) for t, h in zip(temps, hums)]
    lsds = [calcular_lsd(t, h) for t, h in zip(temps, hums)]
    frost_points = [(calcular_frost_point(tdp) if calcular_frost_point(tdp) is not None else np.nan) for tdp in tdps]

    z_temps = [calcular_z_score(t, stats_t.get("Media",0), stats_t.get("StdDev",1)) for t in temps]
    z_hums = [calcular_z_score(h, stats_h.get("Media",0), stats_h.get("StdDev",1)) for h in hums]

    riesgo_hora = [1 if h > 90 else 0 for h in hums]
    horas_riesgo_total = sum(riesgo_hora)
    nivel_riesgo_dia = calcular_riesgo_wallin(horas_riesgo_total, t_media)

    _diffs = np.diff(temps)
    deltas_t = np.concatenate(([0.0], _diffs))
    
    gdd = calcular_gdd(t_max, t_min)
    ch = calcular_horas_frio(temps)
    chu = calcular_chu_maiz(t_min, t_max)
    
    heat_indices = [calcular_heat_index(t, h) for t, h in zip(temps, hums)]
    eto = calcular_eto_hargreaves(t_min, t_max, t_media, 15.0)

    df_horario = pd.DataFrame({
        "Hora_Medicion": list(horas),
        "Timestamp": fechas,
        "T_Bulbo_Seco_C": list(temps),
        "Humedad_Rel_Percent": list(hums),
        "VPD_kPa": list(vpds),
        "Punto_Rocio_C": list(tdps),
        "T_Bulbo_Humedo_C": list(twbs),
        "Presion_Vapor_Sat_kPa": list(es_arr),
        "Presion_Vapor_Act_kPa": list(ea_arr),
        "Humedad_Abs_g_m3": list(has),
        "Humedad_Esp_kg_kg": list(qs),
        "Relacion_Mezcla_kg_kg": list(rs),
        "Entalpia_kJ_kg": list(ents),
        "Heat_Index_C": list(heat_indices),
        "LSD_kPa": list(lsds),
        "Frost_Point_C": list(frost_points),
        "Z_Score_Temp": list(z_temps),
        "Z_Score_Hum": list(z_hums),
        "Delta_T_C_h": list(deltas_t)
    })
    
    df_resumen = pd.DataFrame({
        "Parametro": [
            "T Max", "T Min", "T Media", "HR Media", 
            "GDD", "Horas Frio", "CHU", 
            "ETo", "VPD Promedio", 
            "Riesgo Enfermedad (Wallin)", "Z-Score T (Max)", "Z-Score T (Min)"
        ],
        "Valor": [
            t_max, t_min, t_media, stats_h.get("Media", 0), 
            gdd, ch, chu, 
            eto, np.mean(vpds), 
            nivel_riesgo_dia, max(z_temps) if z_temps else 0, min(z_temps) if z_temps else 0
        ],
        "Unidad": [
            "°C", "°C", "°C", "%", 
            "°C d", "h", "-", 
            "mm/d", "kPa", 
            "Nivel (0-4)", "SD", "SD"
        ]
    })
    
    return df_horario, df_resumen
