import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "agronomica.db")

def init_db():
    """Inicializa la base de datos con la tabla de mediciones para múltiples nodos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Tabla: mediciones
    # node_id: Identificador de la planta/nodo (ej: "Tomate_1")
    # timestamp: Fecha y hora ISO
    sql_create = """
    CREATE TABLE IF NOT EXISTS mediciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        node_id TEXT NOT NULL,
        temp_c REAL,
        humidity_rh REAL,
        radiation_w_m2 REAL
    );
    """
    cursor.execute(sql_create)
    
    # Índice para búsquedas rápidas por nodo y fecha
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_node_time ON mediciones(node_id, timestamp);")
    
    conn.commit()
    conn.close()
    print(f"🗄️  Base de datos inicializada: {DB_FILE}")

def guardar_mediciones(datos_lista):
    """
    Inserta una lista de diccionarios o tuplas.
    Formato esperado: [(ts, node, t, h, r), ...]
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    sql = "INSERT INTO mediciones (timestamp, node_id, temp_c, humidity_rh, radiation_w_m2) VALUES (?, ?, ?, ?, ?)"
    cursor.executemany(sql, datos_lista)
    
    conn.commit()
    conn.close()
    print(f" {len(datos_lista)} registros insertados en DB.")

def leer_datos_nodo(node_id):
    """Retorna DataFrame o lista de diccionarios con datos de un nodo."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    sql = "SELECT timestamp, temp_c, humidity_rh, radiation_w_m2 FROM mediciones WHERE node_id = ? ORDER BY timestamp ASC"
    cursor.execute(sql, (node_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_nodos_activos():
    """Devuelve lista de node_ids únicos."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT node_id FROM mediciones")
    nodos = [row[0] for row in cursor.fetchall()]
    conn.close()
    return nodos

if __name__ == "__main__":
    # Test rápido al ejecutar directamente
    init_db()
