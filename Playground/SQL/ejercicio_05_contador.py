import sqlite3

DB_FILE = "playground.db"

def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # 1. Preguntar qué tipo quieren contar
    tipo_buscado = input("¿Qué tipo de sensor quieres contar? (Ej: Temperatura): ")

    # 2. Ejecutar la consulta (Usa SELECT COUNT(*) o trae todos y cuenta en Python)
    # sql = "SELECT COUNT(*) FROM sensores WHERE tipo = ?"
    # cursor.execute(sql, (tipo_buscado,))
    
    # 3. Obtener el resultado
    # resultado = cursor.fetchone() # Devuelve una tupla (cantidad,)
    # cantidad = resultado[0]

    # print(f"Hay {cantidad} sensores de tipo {tipo_buscado}")

    conn.close()

if __name__ == "__main__":
    main()
