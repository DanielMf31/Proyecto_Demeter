import sqlite3

DB_FILE = "playground.db"

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f" Conectado a {DB_FILE}")

    # 1. Pedir datos al usuario (input)
    nombre = input("Introduzca su nombre: ")
    tipo = input("Introduzca su tipo de sexualidad: ")
    valor = input("Introduzca su tamaño de pene:")
    # 2. Insertar en la base de datos de forma segura (usando ?)
    sql = "INSERT INTO sensores (nombre, tipo, valor) VALUES (?, ?, ?)"
    datos = (nombre, tipo, valor)
    cursor.execute(sql, datos)

    # 3. Guardar cambios (commit) y cerrar
    conn.commit()
    conn.close()
    
    print("¡Datos insertados! (Verifica con DB Browser)")

if __name__ == "__main__":
    main()
