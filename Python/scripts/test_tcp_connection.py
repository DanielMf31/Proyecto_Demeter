import asyncio
import json
import socket

async def test_connection():
    uri = "127.0.0.1"
    port = 8888
    print(f"🍌 Nano Banana Testing Connection to {uri}:{port}...")

    try:
        reader, writer = await asyncio.open_connection(uri, port)
        print("✅ TCP Connection Successful! Pipe is open.")
        
        # Test sending a PING
        msg = {"type": "PING", "payload": {"target_id": 1}}
        print(f"📤 Sending: {json.dumps(msg)}")
        writer.write((json.dumps(msg) + "\n").encode())
        await writer.drain()
        
        # Read response (with timeout)
        print("📥 Waiting for response...")
        data = await asyncio.wait_for(reader.readline(), timeout=5.0)
        if data:
            print(f"✅ Received: {data.decode().strip()}")
        else:
            print("❌ Connection closed by server without data.")
            
        print("Closing connection...")
        writer.close()
        await writer.wait_closed()
        
    except ConnectionRefusedError:
        print("❌ Connection Refused! Is the Service running?")
        print("   -> Run 'python3 src/proyecto_demeter/core/async_service.py' first.")
    except asyncio.TimeoutError:
        print("❌ Timeout! Service accepted connection but sent no data back.")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
