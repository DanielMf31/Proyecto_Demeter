import sqlite3
import os

# 1. Definir el nombre del archivo de base de datos
DB_FILE = "playground.db"

# Borrar si ya existe para empezar limpio (solo para aprendizaje)
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
    print(f"  Archivo anterior '{DB_FILE}' borrado.")

# 2. Conectar a la Base de Datos
# (Si no existe el archivo, sqlite3 lo crea automáticamente)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print(f" Conectado a la base de datos: {DB_FILE}")

# 3. Crear una Tabla (El "Excel")
# Vamos a crear una tabla llamada 'sensores'
# Columnas:
#   id: Un número único para identificar cada fila (PRIMARY KEY)
#   nombre: Texto (e.g., "Sensor Salón")
#   tipo: Texto (e.g., "Temperatura")
#   valor: Número Real (con decimales)

sql_crear_tabla = """
CREATE TABLE IF NOT EXISTS sensores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    valor REAL
);
"""

cursor.execute(sql_crear_tabla)
print("🏗️  Tabla 'sensores' creada exitosamente.")

# 4. Cerrar la conexión (Importante)
conn.close()
print("🔒 Conexión cerrada.")
print("\n👉 Ahora puedes abrir 'playground.db' con DB Browser para verla vacía.")
