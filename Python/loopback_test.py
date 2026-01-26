
import serial
import time
import sys

# Configuración
PORT = '/dev/ttyS0'  # O '/dev/serial0'
BAUD = 115200

def test_loopback():
    print(f"=== PRUEBA DE LOOPBACK UART RASPBERRY PI ===")
    print(f"Puerto: {PORT} @ {BAUD}")
    print("INSTRUCCIONES:")
    print("1. Conecta un cable puente (jumper) entre el pin TX (GPIO 14) y RX (GPIO 15).")
    print("2. Si no lo has hecho, hazlo AHORA.")
    print("------------------------------------------------")
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print(f"Puerta {PORT} abierto correctamente.")
    except Exception as e:
        print(f"ERROR abriendo puerto: {e}")
        return

    message = "Hola Loopback!\n"
    print(f"Enviando: {message.strip()}")
    
    try:
        # Enviar
        ser.write(message.encode('utf-8'))
        
        # Esperar y leer
        time.sleep(0.1)
        received = ser.readline().decode('utf-8').strip()
        
        if received:
            print(f"Recibido: {received}")
            if received == "Hola Loopback!":
                print("\n✅ ÉXITO: El puerto UART funciona correctamente.")
                print("   Si esto funciona pero no comunica con el ESP32, revisa:")
                print("   1. Cables cruzados (TX RPi -> RX ESP32)")
                print("   2. TIERRA (GND) compartida obligatoriamente.")
            else:
                print("\n⚠️ AVISO: Se recibieron datos pero no coinciden exactamente.")
        else:
            print("\n❌ FALLO: No se recibió nada.")
            print("   Posibles causas:")
            print("   - Cable TX-RX no conectado.")
            print("   - Puerto incorrecto (prueba /dev/ttyAMA0).")
            print("   - UART no habilitado en raspi-config.")
            
    except Exception as e:
        print(f"Error durante la prueba: {e}")
    finally:
        ser.close()

if __name__ == "__main__":
    test_loopback()
