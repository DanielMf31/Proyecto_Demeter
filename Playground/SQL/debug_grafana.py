import sqlite3
import time
from datetime import datetime

DB_FILE = "/tmp/grafana_demo.db"

def check_data():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print(f"--- 🕵️ Debugging {DB_FILE} ---")
    
    # 1. Ver cuántas filas hay
    cursor.execute("SELECT count(*) FROM mediciones")
    count = cursor.fetchone()[0]
    print(f"Total filas: {count}")
    
    # 2. Ver las últimas 5 filas y cómo SQLite las transforma
    print("\nÚltimos 5 datos (Raw vs UNIX):")
    print(f"{'ID':<5} | {'Fecha Raw (DB)':<25} | {'SQLite strftime(\"%s\")':<20} | {'Valor':<10}")
    print("-" * 70)
    
    cursor.execute("""
        SELECT id, fecha, strftime('%s', fecha), valor 
        FROM mediciones 
        ORDER BY id DESC LIMIT 5
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        id_val, fecha, unix_time, valor = row
        print(f"{id_val:<5} | {fecha:<25} | {unix_time:<20} | {valor:<10}")

    # 3. Comparar con hora actual
    now_unix = int(time.time())
    print("-" * 70)
    print(f"Hora actual del sistema (UNIX): {now_unix}")
    
    if rows:
        last_unix = int(rows[0][2]) if rows[0][2] else 0
        diff = now_unix - last_unix
        print(f"Diferencia (Ahora - Último dato): {diff} segundos")
        if abs(diff) > 3600:
            print("⚠️ ALERTA: Diferencia de >1 hora. Revisa la Zona Horaria.")
        elif diff < -5:
            print("⚠️ ALERTA: El dato está en el FUTURO (Grafana no lo verá hasta entonces).")
        else:
            print("✅ El tiempo parece correcto.")

    conn.close()

if __name__ == "__main__":
    check_data()
