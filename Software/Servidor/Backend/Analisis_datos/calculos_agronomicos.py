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
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))

def calcular_presion_vapor_actual(T, HR):
    es = calcular_presion_vapor_saturacion(T)
    return es * (HR / 100.0)

def calcular_vpd(T, HR):
    es = calcular_presion_vapor_saturacion(T)
    ea = es * (HR / 100.0)
    return max(0, es - ea)

def calcular_punto_rocio(T, HR):
    ea = calcular_presion_vapor_actual(T, HR)
    if ea <= 0.0001: return -999 
    ln_val = np.log(ea / 0.6108)
    tdp = (237.3 * ln_val) / (17.27 - ln_val)
    return tdp

def calcular_humedad_absoluta(T, HR):
    ea = calcular_presion_vapor_actual(T, HR)
    tk = T + 273.15
    return (2165 * ea) / tk

def calcular_humedad_especifica(T, HR, P_kpa=101.3):
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - 0.378 * ea)

def calcular_relacion_mezcla(T, HR, P_kpa=101.3):
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - ea)

def calcular_entalpia(T, HR, P_kpa=101.3):
    r = calcular_relacion_mezcla(T, HR, P_kpa)
    return 1.006 * T + r * (2501 + 1.86 * T)

def calcular_bulbo_humedo_stull(T, HR):
    term1 = T * np.arctan(0.151977 * (HR + 8.313659)**0.5)
    term2 = np.arctan(T + HR)
    term3 = -np.arctan(HR - 1.676331)
    term4 = 0.00391838 * (HR**1.5) * np.arctan(0.023101 * HR)
    term5 = -4.686035
    return term1 + term2 + term3 + term4 + term5

# --- 3. FENOLOGÍA Y TIEMPO (Sin radiación) ---
def calcular_gdd(t_max, t_min, t_base=10):
    gdd = ((t_max + t_min) / 2) - t_base
    return max(0, gdd)

def calcular_horas_frio(temperaturas_horarias, umbral=7.2):
    return sum(1 for t in temperaturas_horarias if 0 < t < umbral)

def calcular_chu_maiz(t_min, t_max):
    y_min = 1.8 * (t_min - 4.4)
    y_max = 3.33 * (t_max - 10) - 0.084 * (t_max - 10)**2
    return (y_max + y_min) / 2

# --- 4. ÍNDICES DE ESTRÉS Y MODELADO ---
def calcular_heat_index(T, HR):
    if T < 27: return T 
    hi = -8.78469475556 + 1.61139411*T + 2.338548838*HR - 0.14611605*T*HR \
         - 0.012308094*T**2 - 0.0164248277*HR**2 + 0.002211732*T**2*HR \
         + 0.00072546*T*HR**2 - 0.000003582*T**2*HR**2
    return hi

def calcular_eto_hargreaves(t_min, t_max, t_media, ra_mm_dia):
    return 0.0023 * ra_mm_dia * (t_media + 17.8) * np.sqrt(max(0, t_max - t_min))

def calcular_lsd(t_aire, hr):
    t_hoja = t_aire - 2.0
    es_hoja = calcular_presion_vapor_saturacion(t_hoja)
    ea_aire = calcular_presion_vapor_actual(t_aire, hr)
    return es_hoja - ea_aire

def calcular_frost_point(t_dp):
    return t_dp if t_dp < 0 else None

def calcular_riesgo_wallin(horas_hr_alta, t_media):
    if horas_hr_alta < 10: return 0
    if 10 <= t_media <= 27:
        if horas_hr_alta >= 10: return 1
        if horas_hr_alta >= 20: return 2
    return 0

def calcular_z_score(val, mu, sigma):
    return (val - mu) / sigma if sigma > 0 else 0

# --- PROCESADOR PRINCIPAL ---
def procesar_dataframe(df_crudo: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Toma un DataFrame crudo con ['timestamp', 'temperature', 'humidity']
    y retorna (df_horario_completo, df_resumen)
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
