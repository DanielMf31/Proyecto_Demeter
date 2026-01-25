
import time
import sys
import logging
import argparse
from uart_service import UARTService
from protocol_engine import ProtocolEngine

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('MainPoC')

# Datos de prueba (Idénticos al ejemplo C++)
TEST_DATA = [
    [1, 1, 0, 1000, 0], # Actuador 1, 1000ms
    [1, 2, 0, 2000, 0], # Actuador 2, 2000ms
    [1, 3, 0, 3000, 0], # Actuador 3, 3000ms
    [1, 4, 0, 4000, 0], # Actuador 4, 4000ms
    [1, 5, 0, 5000, 0]  # Actuador 5, 5000ms
]

def main():
    parser = argparse.ArgumentParser(description='PoC Transmisor UART para Proyecto Demeter')
    parser.add_argument('--port', type=str, help='Puerto Serial (Sobrescribe config)')
    parser.add_argument('--baud', type=int, help='Baudrate (Sobrescribe config)')
    args = parser.parse_args()
    
    # Cargar Configuración
    import json
    import os
    from pathlib import Path
    
    # Defaults
    port = '/dev/ttyUSB0'
    baud = 115200
    
    # Intentar leer config
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                port = config.get('uart', {}).get('port', port)
                baud = config.get('uart', {}).get('baudrate', baud)
            logger.info(f"Configuración cargada de {config_path}")
        except Exception as e:
            logger.warning(f"Error leyendo config: {e}")
    else:
        logger.info("No se encontró archivo de configuración, usando defaults.")

    # Argumentos tienen prioridad
    if args.port:
        port = args.port
    if args.baud:
        baud = args.baud

    logger.info("=== INICIANDO PoC TRANSMISOR (PYTHON) ===")
    logger.info(f"Puerto: {port}, Baud: {baud}")

    # 1. Inicializar Servicio UART
    uart = UARTService(port=port, baudrate=baud)
    if not uart.connect():
        logger.critical("No se pudo conectar al puerto serial. Abortando.")
        sys.exit(1)

    # 2. Inicializar Motor de Protocolo
    engine = ProtocolEngine(uart)
    engine.configure_data(TEST_DATA)

    # 3. Iniciar Protocolo
    try:
        engine.start_protocol()
        
        # Bucle principal
        while True:
            engine.process()
            
            state = engine.state
            
            # Verificar condiciones de salida
            if state == 5: # COMUNICACION_COMPLETADA
                logger.info(">>> ÉXITO: Ciclo de protocolo completado correctamente <<<")
                break
            
            if state == 6: # ERROR_COMUNICACION
                logger.error(">>> FALLO: Error de comunicación (Verificación fallida) <<<")
                break
                
            if state == 7: # ERROR_TIMEOUT
                logger.error(">>> FALLO: Timeout esperando respuesta <<<")
                break
                
            time.sleep(0.01) # Simular loop de Arduino

    except KeyboardInterrupt:
        logger.info("\nInterrupción de usuario. Cerrando...")
    finally:
        uart.close()
        logger.info("Fin de la prueba.")

if __name__ == "__main__":
    main()
