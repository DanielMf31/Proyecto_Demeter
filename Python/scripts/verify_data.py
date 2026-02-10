import asyncio
import aiosqlite
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from proyecto_demeter.data.database import DatabaseManager

async def check_data():
    db_path = os.path.join(os.path.dirname(__file__), '../data/demeter_data.db')
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("   Make sure the service has been started at least once.")
        return

    print(f"✅ Database found: {db_path}")
    
    db = DatabaseManager(db_path)
    # We cheat and use the internal method or just raw sql if easier, 
    # but let's use the public API if possible or just connect manually for a script.
    
    async with aiosqlite.connect(db_path) as conn:
        async with conn.execute("SELECT COUNT(*) FROM sensor_readings") as cursor:
            count = await cursor.fetchone()
            print(f"📊 Total Records: {count[0]}")
        
        print("\n📋 Latest 10 Readings:")
        print(f"{'ID':<5} {'Timestamp':<25} {'Node':<5} {'Temp':<10} {'Hum':<10}")
        print("-" * 60)
        
        async with conn.execute("SELECT id, timestamp, node_id, temperature, humidity FROM sensor_readings ORDER BY id DESC LIMIT 10") as cursor:
            async for row in cursor:
                print(f"{row[0]:<5} {row[1]:<25} {row[2]:<5} {row[3]:<10.2f} {row[4]:<10.2f}")

if __name__ == "__main__":
    asyncio.run(check_data())
