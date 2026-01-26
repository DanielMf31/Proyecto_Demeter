
import sys
import json
import os
import glob
from pathlib import Path

# Intentar importar serial.tools.list_ports
try:
    import serial.tools.list_ports
except ImportError:
    print("Error: pyserial no está instalado. Ejecuta 'pip install pyserial'")
    sys.exit(1)

CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"

def detect_serial_ports():
    """
    Detecta puertos seriales disponibles.
    Retorna una lista de tuplas (device, description).
    """
    ports = serial.tools.list_ports.comports()
    result = []
    
    # Prioridad: /dev/serial0 (Raspberry Pi UART principal)
    # Check if /dev/serial0 exists explicitly
    if os.path.exists('/dev/serial0'):
        result.append(('/dev/serial0', 'Raspberry Pi Default UART'))
        
    for port in ports:
        # Evitar duplicados si serial0 apunta a ttyS0/ttyAMA0
        if port.device not in [r[0] for r in result]:
            result.append((port.device, port.description))
            
    return result

def save_config(port, baudrate=115200):
    """Guarda la configuración en JSON"""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(parents=True)
        
    config_data = {
        "uart": {
            "port": port,
            "baudrate": baudrate,
            "timeout": 1
        }
    }
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"✔ Configuración guardada en: {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"✘ Error al guardar configuración: {e}")
        return False

def main():
    print("=== Detección y Configuración de Puerto UART ===")
    
    print("Buscando puertos disponibles...")
    available_ports = detect_serial_ports()
    
    if not available_ports:
        print("⚠ No se detectaron puertos seriales.")
        # Fallback manual
        print("Configurando puerto por defecto /dev/serial0 (esperando que se habilite tras reinicio).")
        save_config("/dev/serial0")
        return

    print(f"Se encontraron {len(available_ports)} puertos:")
    for i, (dev, desc) in enumerate(available_ports):
        print(f"  [{i+1}] {dev} - {desc}")
        
    # Selección automática inteligente
    # Si existe serial0, usarlo. Si hay USB, preferirlo (para debug en PC).
    selected_port = None
    
    # 1. Buscar /dev/serial0 (RPi Native)
    for dev, desc in available_ports:
        if dev == "/dev/serial0":
            selected_port = dev
            break
            
    # 2. Si no, buscar USB (PC Debug)
    if not selected_port:
        for dev, desc in available_ports:
            if "USB" in dev or "USB" in desc:
                selected_port = dev
                break
                
    # 3. Fallback al primero
    if not selected_port:
        selected_port = available_ports[0][0]
        
    print(f"\nPuerto seleccionado automáticamente: {selected_port}")
    
    if save_config(selected_port):
        print("Configuración completada exitosamente.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
