import sqlite3

DB_FILE = "playground.db"

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Mostrar todos los sensores para saber cuál borrar
    print("--- Sensores Disponibles ---")
    cursor.execute("SELECT id, nombre FROM sensores")
    for fila in cursor.fetchall():
        print(f"ID: {fila[0]} | Nombre: {fila[1]}")
    print("--------------------------")

    # 2. Pedir ID
    id_borrar = input("Introduce el ID del sensor a borrar: ")

    # 3. Confirmación de seguridad
    confirmacion = input(f"¿Seguro que quieres borrar el ID {id_borrar}? (s/n): ")

    if confirmacion.lower() == 's':
        # 4. BORRAR
        # sql = "DELETE FROM ..."
        # cursor.execute(...)
        # conn.commit()
        print("🗑️  Sensor borrado.")
    else:
        print("❌ Operación cancelada.")

    conn.close()

if __name__ == "__main__":
    main()
