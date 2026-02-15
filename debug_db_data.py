import sqlite3
import os
from datetime import datetime

# Path to DB
db_path = "Python/data/demeter_data.db"

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"--- Checking Data in {db_path} ---")
print(f"Current System Time: {datetime.now()}")

# count rows
cursor.execute("SELECT count(*) FROM sensor_readings")
count = cursor.fetchone()[0]
print(f"Total Rows: {count}")

# Last 5 rows
print("\n--- Last 5 Readings ---")
cursor.execute("SELECT id, timestamp, node_id, temperature, humidity FROM sensor_readings ORDER BY timestamp DESC LIMIT 5")
rows = cursor.fetchall()

if not rows:
    print("No data found!")
else:
    for row in rows:
        print(f"ID: {row[0]} | Time: {row[1]} | Node: {row[2]} | Temp: {row[3]} | Hum: {row[4]}")
        # Test converting time
        try:
             cursor.execute(f"SELECT strftime('%s', '{row[1]}')")
             epoch = cursor.fetchone()[0]
             print(f"   -> Epoch (Seconds): {epoch}")
        except Exception as e:
            print(f"   -> Error converting time: {e}")

conn.close()
