import sqlite3
import time
import random
import os
import logging
from datetime import datetime

# --- CONFIGURACIÓN DE LOGS ---
# Creamos la carpeta 'logs' si no existe
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

from logging.handlers import TimedRotatingFileHandler

# --- CONFIGURACIÓN DE LOGS (Con Rotación Automática) ---
# Creamos la carpeta 'logs' si no existe
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Usamos un nombre fijo "demeter_service.log".
# Python renombrará automáticamente los viejos a "demeter_service.log.YYYY-MM-DD"
log_path = os.path.join(LOG_DIR, "demeter_service.log")

# Configuración del Rotador:
# - when="midnight": Cierra el archivo y crea uno nuevo a media noche.
# - backupCount=7: Mantiene solo los últimos 7 días. Borra los más viejos.
rotating_handler = TimedRotatingFileHandler(
    filename=log_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8"
)
rotating_handler.suffix = "%Y-%m-%d" # Sufijo para los archivos viejos

# Configuramos el logging para que escriba en ARCHIVO (rotativo) y en CONSOLA
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        rotating_handler,
        logging.StreamHandler()
    ]
)

# Configuración Base de Datos
DB_FILE = "/tmp/grafana_demo.db"
SENSOR_TIPO = "Temperatura"

def inicializar_db():
    """Crea la tabla si no existe"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # IMPORTANTE: Eliminamos WAL para evitar problemas de permisos en archivos compartidos en /tmp
    # cursor.execute("PRAGMA journal_mode=WAL;") 
    
    # IMPORTANTE: Grafana necesita una columna de tiempo.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mediciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            tipo TEXT,
            valor REAL,
            fecha DATETIME
        )
    """)
    conn.commit()
    conn.close()
    
    # PERMISOS PARA GRAFANA
    # Grafana corre con otro usuario (normalmente 'grafana').
    # Para que pueda leer este archivo en tu carpeta personal, necesitamos darle permisos amplios.
    # En un entorno real, esto se maneja con grupos, pero para Playground: 666 (Read/Write All).
    try:
        os.chmod(DB_FILE, 0o666)
        logging.info(f"🔓 Permisos actualizados a 666 para: {DB_FILE}")
    except Exception as e:
        logging.error(f"⚠️ No se pudieron cambiar permisos automáticamente: {e}")

# Configuración de Sensores (Nombre, MinTemp, MaxTemp)
SENSORES = [
    ("Sensor_Patio", 10.0, 20.0),    # Más frío
    ("Sensor_Cocina", 10.0, 20.0),   # Más caliente
    ("Sensor_Salon", 10.0, 20.0)     # Intermedio
]

def insertar_dato():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Fecha actual en UTC (Universal Time Coordinated)
    # Usamos la misma marca de tiempo para los 3 sensores en este ciclo
    fecha_actual = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
# Configuración de Variación (¡Toca aquí para cambiar lo rápido que se mueven!)
VARIACION_MEDIA = 2.5  # Cuánto suele cambiar la temperatura de media (Magnitud)
VARIACION_STD = 0.5    # Cuánto varía ese cambio (Desviación Estándar)

# Estado actual de los sensores
ESTADO_SENSORES = {
    "Sensor_Patio": 15.0,
    "Sensor_Cocina": 27.5,
    "Sensor_Salon": 22.0
}

def insertar_dato():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    fecha_actual = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"--- ⏱️ Ciclo: {fecha_actual} ---")
    
    # --- 1. SENSORES DE TEMPERATURA (Ya existente) ---
    for nombre, t_min, t_max in SENSORES:
        # Recuperamos el valor anterior
        valor_anterior = ESTADO_SENSORES[nombre]
        
        # 1. Calculamos cuánto va a cambiar (Magnitud normal + Direccion aleatoria)
        magnitud = random.gauss(VARIACION_MEDIA, VARIACION_STD)
        direccion = random.choice([-1, 1]) # 50% subir, 50% bajar
        delta = magnitud * direccion
        
        # 2. Aplicamos el cambio
        nuevo_valor = valor_anterior + delta
        
        # 3. Rebote en los límites (para que no se salga nunca)
        if nuevo_valor < t_min: 
            nuevo_valor = t_min + abs(delta) # Rebotar hacia arriba
        if nuevo_valor > t_max: 
            nuevo_valor = t_max - abs(delta) # Rebotar hacia abajo
        
        # Guardamos el nuevo estado
        ESTADO_SENSORES[nombre] = nuevo_valor
        valor_final = round(nuevo_valor, 2)
        
        logging.info(f"📡 Insertando: {nombre:<15} | Temp: {valor_final:.2f}°C")
        
        cursor.execute(
            "INSERT INTO mediciones (nombre, tipo, valor, fecha) VALUES (?, ?, ?, ?)",
            (nombre, "Temperatura", valor_final, fecha_actual)
        )

    # --- 2. BATERÍA (Simulación de descarga) ---
    # La batería baja 0.1% cada ciclo, y se recarga al llegar al 20%
    nivel_bateria = ESTADO_SENSORES.get("Bateria_General", 100.0)
    nivel_bateria -= 0.5 # Descarga rápida para que se vea en la demo
    if nivel_bateria < 20.0: nivel_bateria = 100.0 # ¡Recarga mágica!
    ESTADO_SENSORES["Bateria_General"] = nivel_bateria
    
    logging.info(f"🔋 Insertando: Bateria_General | {nivel_bateria:.1f}%")
    cursor.execute(
        "INSERT INTO mediciones (nombre, tipo, valor, fecha) VALUES (?, ?, ?, ?)",
        ("Bateria_General", "Bateria", nivel_bateria, fecha_actual)
    )

    # --- 3. HUMEDAD (Correlacionada inversamente con Tª) ---
    # Si hace calor, baja la humedad.
    humedad = 100.0 - ESTADO_SENSORES["Sensor_Patio"] * 1.5 + random.uniform(-2, 2)
    logging.info(f"💧 Insertando: Humedad_Patio   | {humedad:.1f}%")
    cursor.execute(
        "INSERT INTO mediciones (nombre, tipo, valor, fecha) VALUES (?, ?, ?, ?)",
        ("Humedad_Patio", "Humedad", humedad, fecha_actual)
    )
    
    conn.commit()
    conn.close()

def main():
    # Obtener ruta absoluta para facilitar configuración en Grafana
    ruta_absoluta = os.path.abspath(DB_FILE)
    logging.info("--- 🏭 Generador de Datos para Grafana ---")
    logging.info(f"📁 Base de Datos: {ruta_absoluta}")
    logging.info(f"📝 Logs guardados en: {log_path}")
    logging.info("------------------------------------------")
    
    inicializar_db()
    
    try:
        while True:
            insertar_dato()
            time.sleep(5) # Esperar 5 segundos
    except KeyboardInterrupt:
        logging.info("\n🛑 Generador detenido.")

if __name__ == "__main__":
    main()
