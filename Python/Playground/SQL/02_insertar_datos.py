import sqlite3
import random
import time

DB_FILE = "playground.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print(f"✅ Conectado a {DB_FILE}")

# 1. Insertar UN DATO manualmente
# VALUES ('Sensor Salón', 'Temperatura', 23.5)
# El 'id' se genera solo porque es AUTOINCREMENT
sql_insert_uno = "INSERT INTO sensores (nombre, tipo, valor) VALUES (?, ?, ?)"

dato_nuevo = ("Sensor Salón", "Temperatura", 23.5)
cursor.execute(sql_insert_uno, dato_nuevo)
print("📥 Insertado: Sensor Salón (23.5°C)")

# 2. Insertar MUCHOS DATOS (Simulación)
print("\n🔄 Generando 5 datos aleatorios...")
nombres = ["Sensor Cocina", "Sensor Baño", "Sensor Jardín"]
tipos = ["Humedad", "Temperatura", "CO2"]

for i in range(5):
    nombre = random.choice(nombres)
    tipo = random.choice(tipos)
    valor = round(random.uniform(10.0, 90.0), 2)
    
    dato = (nombre, tipo, valor)
    cursor.execute(sql_insert_uno, dato)
    print(f"   ➕ Insertado: {nombre} - {tipo}: {valor}")
    time.sleep(0.5)

# 3. Guardar cambios (COMMIT)
# Si no haces commit, los datos solo existen en memoria y se pierden al cerrar.
conn.commit()
print("\n💾 Cambios guardados (COMMIT realizado).")

conn.close()
