import numpy as np
import math
import datetime
import os
import pandas as pd
import sys

# Add SQL folder to path
sys.path.append(os.path.join(os.path.dirname(__file__), "SQL"))
try:
    from db_agronomica import init_db, guardar_mediciones, leer_datos_nodo, obtener_nodos_activos
except ImportError:
    # Fallback absolute path for redundancy
    sys.path.append("/home/danielmf31/Documentos/PlatformIO/Projects/Proyecto_Demeter/Python/Playground/SQL")
    from db_agronomica import init_db, guardar_mediciones, leer_datos_nodo, obtener_nodos_activos

# --- 1. ESTADÍSTICA DESCRIPTIVA ---
def calcular_estadisticas(datos):
    """Calcula media, desviación estándar, CV y SEM."""
    if len(datos) == 0: return {}
    arr = np.array(datos)
    mu = np.mean(arr)
    sigma = np.std(arr, ddof=1)  # Muestra
    cv = (sigma / mu) * 100 if mu != 0 else 0
    sem = sigma / np.sqrt(len(datos))
    return {"Media": mu, "StdDev": sigma, "CV": cv, "SEM": sem}

# --- 2. TERMODINÁMICA DEL AGUA Y AIRE ---
def calcular_presion_vapor_saturacion(T):
    """Ecuación de Tetens/Magnus. T en Celsius. Retorna kPa."""
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))

def calcular_presion_vapor_actual(T, HR):
    """e_a = e_s * (HR / 100)."""
    es = calcular_presion_vapor_saturacion(T)
    return es * (HR / 100.0)

def calcular_vpd(T, HR):
    """VPD = e_s - e_a. Retorna kPa."""
    es = calcular_presion_vapor_saturacion(T)
    ea = es * (HR / 100.0)
    return max(0, es - ea)

def calcular_punto_rocio(T, HR):
    """Calcula T_dp. T en Celsius, HR en %."""
    ea = calcular_presion_vapor_actual(T, HR)
    # Evitar log de 0 o negativo
    if ea <= 0.0001: return -999 
    numerador = 17.27 - np.log(ea / 0.6108)
    # Correccion formula logaritmica inversa de Magnus
    # Tdp = (237.3 * ln(ea/0.6108)) / (17.27 - ln(ea/0.6108))
    ln_val = np.log(ea / 0.6108)
    tdp = (237.3 * ln_val) / (17.27 - ln_val)
    return tdp

def calcular_humedad_absoluta(T, HR):
    """g/m3."""
    ea = calcular_presion_vapor_actual(T, HR)
    tk = T + 273.15
    return (2165 * ea) / tk

def calcular_humedad_especifica(T, HR, P_kpa=101.3):
    """kg/kg aire húmedo."""
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - 0.378 * ea)

def calcular_relacion_mezcla(T, HR, P_kpa=101.3):
    """kg/kg aire seco."""
    ea = calcular_presion_vapor_actual(T, HR)
    return (0.622 * ea) / (P_kpa - ea)

def calcular_entalpia(T, HR, P_kpa=101.3):
    """kJ/kg."""
    r = calcular_relacion_mezcla(T, HR, P_kpa)
    return 1.006 * T + r * (2501 + 1.86 * T)

def calcular_bulbo_humedo_stull(T, HR):
    """Aproximación de Stull para T_wb. T en Celsius, HR en %."""
    term1 = T * np.arctan(0.151977 * (HR + 8.313659)**0.5)
    term2 = np.arctan(T + HR)
    term3 = -np.arctan(HR - 1.676331)
    term4 = 0.00391838 * (HR**1.5) * np.arctan(0.023101 * HR)
    term5 = -4.686035
    return term1 + term2 + term3 + term4 + term5

# --- 3. FENOLOGÍA Y TIEMPO ---
def calcular_gdd(t_max, t_min, t_base=10):
    gdd = ((t_max + t_min) / 2) - t_base
    return max(0, gdd)

def calcular_dli(radiacion_solar_horaria_w_m2):
    """
    Estimación simple de DLI (mol/m2/día).
    1 W/m2 ~ 2.02 µmol/m2/s para luz solar (PAR).
    """
    # Sumar W/m2 de todas las horas y convertir.
    # DLI = sum(W/m2) * 3600s/h * 2.02 / 1,000,000
    suma_rad = sum(radiacion_solar_horaria_w_m2)
    return (suma_rad * 3600 * 2.02) / 1000000

def calcular_dtr(t_max, t_min):
    return t_max - t_min

def calcular_horas_frio(temperaturas_horarias, umbral=7.2):
    return sum(1 for t in temperaturas_horarias if 0 < t < umbral)

def calcular_chu_maiz(t_min, t_max):
    y_min = 1.8 * (t_min - 4.4)
    y_max = 3.33 * (t_max - 10) - 0.084 * (t_max - 10)**2
    return (y_max + y_min) / 2

# --- 4. ÍNDICES DE ESTRÉS Y MODELADO ---
def calcular_heat_index(T, HR):
    """Rothfusz (simplificado/completo según NOAA). Solo válido si T > 27°C, HR > 40%."""
    if T < 27: return T # Retorna T si no aplica
    
    hi = -8.78469475556 + 1.61139411*T + 2.338548838*HR - 0.14611605*T*HR \
         - 0.012308094*T**2 - 0.0164248277*HR**2 + 0.002211732*T**2*HR \
         + 0.00072546*T*HR**2 - 0.000003582*T**2*HR**2
    return hi

def calcular_eto_hargreaves(t_min, t_max, t_media, ra_mm_dia):
    """ETo en mm/día. Ra depende de latitud/día (simulado aquí)."""
    return 0.0023 * ra_mm_dia * (t_media + 17.8) * np.sqrt(t_max - t_min)

def calcular_lsd(t_aire, hr):
    """Leaf Saturation Deficit. Asume T_hoja = T_aire - 2°C (transpiración)."""
    t_hoja = t_aire - 2.0
    es_hoja = calcular_presion_vapor_saturacion(t_hoja)
    ea_aire = calcular_presion_vapor_actual(t_aire, hr)
    return es_hoja - ea_aire

def calcular_frost_point(t_dp):
    """Punto de escarcha es T_dp si T_dp < 0."""
    return t_dp if t_dp < 0 else None

def calcular_riesgo_wallin(horas_hr_alta, t_media):
    """
    Modelo simplificado: Si HR > 90% por N horas.
    Depende de T_media. Ejemplo para papa/tizón tardío.
    """
    if horas_hr_alta < 10: return 0
    if 10 <= t_media <= 27:
        if horas_hr_alta >= 10: return 1
        if horas_hr_alta >= 20: return 2
    return 0

# --- 5. MÉTRICAS DE ANOMALÍA ---
def calcular_z_score(val, mu, sigma):
    return (val - mu) / sigma if sigma > 0 else 0

def calcular_skewness(datos, mu, sigma):
    if sigma == 0: return 0
    n = len(datos)
    sum_cubos = sum((x - mu)**3 for x in datos)
    return (sum_cubos / n) / (sigma**3)

def calcular_kurtosis(datos, mu, sigma):
    if sigma == 0: return 0
    n = len(datos)
    sum_cuartas = sum((x - mu)**4 for x in datos)
    return ((sum_cuartas / n) / (sigma**4)) - 3

def calcular_tasa_cambio(datos):
    """Diferencia entre hora actual y anterior."""
    deltas = []
    for i in range(1, len(datos)):
        deltas.append(datos[i] - datos[i-1])
    return deltas


# --- SIMULACIÓN Y REPORTE ---
def generar_datos_simulados_multi_nodo():
    """Genera datos para 3 plantas con diferentes condiciones."""
    init_db()
    
    nodos = [
        {"id": "Planta_Control_A", "t_base": 17.5, "h_base": 65, "rad_factor": 1.0},
        {"id": "Planta_Sequia_B", "t_base": 19.0, "h_base": 45, "rad_factor": 1.1}, # Más calor, menos humedad
        {"id": "Planta_Sombra_C", "t_base": 16.0, "h_base": 75, "rad_factor": 0.6}, # Menos luz, más fresco
    ]
    
    todas_mediciones = []
    horas = np.arange(24)
    
    for nodo in nodos:
        # Variaciones por nodo
        temps = nodo["t_base"] - 7.5 * np.cos((horas - 4) * 2 * np.pi / 24)
        temps += np.random.normal(0, 0.5, 24)
        
        hums = nodo["h_base"] + 25 * np.cos((horas - 4) * 2 * np.pi / 24)
        hums += np.random.normal(0, 2, 24)
        hums = np.clip(hums, 0, 100)
        
        rads = 800 * nodo["rad_factor"] * np.exp(-0.5 * ((horas - 12) / 3)**2)
        rads = np.where(rads < 10, 0, rads)

        # Preparar para DB: (ts, node, t, h, r)
        base_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for h, t, hum, r in zip(horas, temps, hums, rads):
            ts = (base_time + datetime.timedelta(hours=int(h))).isoformat()
            todas_mediciones.append((datetime.datetime.now().strftime("%Y-%m-%dT%H:00:00"), nodo["id"], float(t), float(hum), float(r)))
            
    # Guardar todo en SQL
    guardar_mediciones(todas_mediciones)
    return [n["id"] for n in nodos]

def procesar_datos_nodo(node_id):
    """Lee de DB y calcula todo para un nodo específico."""
    raw_data = leer_datos_nodo(node_id) # Lista de tuplas (ts, t, h, r)
    if not raw_data: return None
    
    # Desempaquetar
    fechas = [row[0] for row in raw_data]
    temps = np.array([row[1] for row in raw_data])
    hums = np.array([row[2] for row in raw_data])
    rads = np.array([row[3] for row in raw_data])
    horas = np.arange(len(raw_data)) # Asumiendo horario continuo 0-23
    
    # --- PROCESAMIENTO AGRONOMICO ---
    # Estadística global del día
    stats_t = calcular_estadisticas(temps)
    stats_h = calcular_estadisticas(hums)
    
    t_max = np.max(temps)
    t_min = np.min(temps)
    t_media = stats_t.get("Media", np.mean(temps) if len(temps) > 0 else 0) # Fallback if stats_t is empty
    
    # Cálculos horarios (arrays)
    vpds = [calcular_vpd(t, h) for t, h in zip(temps, hums)]
    tdps = [calcular_punto_rocio(t, h) for t, h in zip(temps, hums)]
    has = [calcular_humedad_absoluta(t, h) for t, h in zip(temps, hums)]
    ents = [calcular_entalpia(t, h) for t, h in zip(temps, hums)]
    twbs = [calcular_bulbo_humedo_stull(t, h) for t, h in zip(temps, hums)]
    
    # Nuevas variables para completar "Biblia de Formulas"
    es_arr = [calcular_presion_vapor_saturacion(t) for t in temps]
    ea_arr = [calcular_presion_vapor_actual(t, h) for t, h in zip(temps, hums)]
    qs = [calcular_humedad_especifica(t, h) for t, h in zip(temps, hums)]
    rs = [calcular_relacion_mezcla(t, h) for t, h in zip(temps, hums)]
    lsds = [calcular_lsd(t, h) for t, h in zip(temps, hums)]
    frost_points = [(calcular_frost_point(tdp) if calcular_frost_point(tdp) is not None else np.nan) for tdp in tdps]

    # Z-Scores Horarios (Anomalías)
    z_temps = [calcular_z_score(t, stats_t.get("Media",0), stats_t.get("StdDev",1)) for t in temps]
    z_hums = [calcular_z_score(h, stats_h.get("Media",0), stats_h.get("StdDev",1)) for h in hums]

    # Riesgo Enfermedad (Wallin simplificado)
    riesgo_hora = [1 if h > 90 else 0 for h in hums]
    horas_riesgo_total = sum(riesgo_hora)
    nivel_riesgo_dia = calcular_riesgo_wallin(horas_riesgo_total, t_media)

    # Tasa cambio (Delta T)
    _diffs = np.diff(temps)
    deltas_t = np.concatenate(([0.0], _diffs))
    
    # Fenología diaria
    gdd = calcular_gdd(t_max, t_min)
    dli = calcular_dli(rads)
    # dtr = calcular_dtr(t_max, t_min)
    ch = calcular_horas_frio(temps)
    chu = calcular_chu_maiz(t_min, t_max)
    
    # Estrés / Anomalías
    heat_indices = [calcular_heat_index(t, h) for t, h in zip(temps, hums)]
    # ETo aproximada (Ra se asume constante para ejemplo, ej. 15 mm/día en verano)
    eto = calcular_eto_hargreaves(t_min, t_max, t_media, 15.0)

    # DataFrame Horario (TODOS los parámetros)
    df_horario = pd.DataFrame({
        "Hora": list(horas), # 0-23
        "Timestamp": fechas,
        "T_Bulbo_Seco_C": list(temps),
        "Humedad_Rel_Percent": list(hums),
        "Radiacion_W_m2": list(rads),
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
    
    # DataFrame Resumen (Incluyendo Riesgo Wallin)
    df_resumen = pd.DataFrame({
        "Parametro": [
            "T Max", "T Min", "T Media", "HR Media", 
            "DLI", "GDD", "Horas Frio", "CHU", 
            "ETo", "VPD Promedio", 
            "Riesgo Enfermedad (Wallin)", "Z-Score T (Max)", "Z-Score T (Min)"
        ],
        "Valor": [
            t_max, t_min, t_media, stats_h["Media"], 
            dli, gdd, ch, chu, 
            eto, np.mean(vpds), 
            nivel_riesgo_dia, max(z_temps), min(z_temps)
        ],
        "Unidad": [
            "°C", "°C", "°C", "%", 
            "mol/m2/d", "°C d", "h", "-", 
            "mm/d", "kPa", 
            "Nivel (0-4)", "SD", "SD"
        ]
    })
    
    return df_horario, df_resumen

def main():
    print("🌱 Iniciando Simulación Multi-Nodo Demeter...")
    
    # 1. Generar Datos en SQL
    nodes = generar_datos_simulados_multi_nodo()
    print(f"📡 Datos generados y guardados en DB para: {nodes}")

    report_path = os.path.join(os.path.dirname(__file__), "Resultados_Simulacion.md")
    excel_path = os.path.join(os.path.dirname(__file__), "Resultados_Simulacion.xlsx")
    
    # Usar ExcelWriter para multiples hojas
    with pd.ExcelWriter(excel_path) as writer:
        md_content = f"# Reporte Multi-Nodo\nFecha: {datetime.datetime.now()}\n\n"
        
        for node in nodes:
            print(f"⚙️ Procesando nodo: {node}...")
            # Leer de DB y calcular
            df_h, df_r = procesar_datos_nodo(node)
            
            if df_h is not None:
                # Guardar en Excel (hoja por nodo)
                sheet_name = node[:30] # Limite caracteres Excel
                df_h.to_excel(writer, sheet_name=f"{sheet_name}", index=False)
                df_r.to_excel(writer, sheet_name=f"{sheet_name}_Res", index=False)
                
                # Agregar al MD
                t_avg = df_r.loc[df_r['Parametro'] == 'T Media', 'Valor'].values[0]
                vpd_avg = df_r.loc[df_r['Parametro'] == 'VPD Promedio', 'Valor'].values[0]
                
                md_content += f"## Nodo: {node}\n"
                md_content += f"- **Temp Media**: {t_avg:.1f} °C\n"
                md_content += f"- **VPD Promedio**: {vpd_avg:.2f} kPa\n\n"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"📊 Excel Multi-Hoja guardado en: {excel_path}")
    print(f"📄 Reporte MD guardado en: {report_path}")

if __name__ == "__main__":
    main()
