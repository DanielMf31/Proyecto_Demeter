import sqlite3

DB_FILE = "playground.db"

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

print(f"✅ Conectado a {DB_FILE}")

# 1. Leer TODOS los datos
# SELECT * FROM sensores
print("\n--- 📖 Leyendo TODOS los datos ---")
cursor.execute("SELECT * FROM sensores")
filas = cursor.fetchall() # Obtiene todas las filas como una lista

# Imprimir bonito
print(f"{'ID':<5} {'NOMBRE':<20} {'TIPO':<15} {'VALOR':<10}")
print("-" * 50)
for fila in filas:
    # fila es una tupla: (1, 'Sensor Salón', 'Temperatura', 23.5)
    id_fila, nombre, tipo, valor = fila
    print(f"{id_fila:<5} {nombre:<20} {tipo:<15} {valor:<10}")

# 2. Filtrar Datos (WHERE)
# "Dame solo los que sean 'Temperatura' y valgan más de 25"
print("\n--- 🔍 Buscando Temperaturas > 25 ---")

sql_filtro = "SELECT * FROM sensores WHERE tipo='Temperatura' AND valor > 25"
cursor.execute(sql_filtro)
filas_filtro = cursor.fetchall()

if not filas_filtro:
    print("❌ No hay sensores que cumplan esa condición.")
else:
    for fila in filas_filtro:
        print(fila)

conn.close()
