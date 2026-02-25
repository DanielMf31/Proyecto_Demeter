import os
import sys

# Agregamos la ruta local por si no hemos ejecutado `pip install -e .`
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "SDK")))

from demeter_sdk import DemeterClient

def main():
    print("=========================================")
    print("🌾 DEMETER PYTHON SDK - INTEGRATION TEST")
    print("=========================================")
    
    if len(sys.argv) < 3:
        print("Uso: python3 test_sdk.py <EXP_ID> <API_KEY>")
        sys.exit(1)
        
    EXP_ID = int(sys.argv[1])
    API_KEY = sys.argv[2]
    BASE_URL = "http://localhost:8000"
    
    print(f"\n1. Inicializando cliente -> {BASE_URL}")
    print(f"Usando API Key: {API_KEY}")
    client = DemeterClient(api_key=API_KEY, base_url=BASE_URL)
    
    print(f"\n2. Testing get_raw_data() para Exp {EXP_ID} (últimos 7 días)...")
    try:
        raw = client.get_raw_data(experimento_id=EXP_ID, dias=7)
        print(f"   [OK] {len(raw)} registros crudos recibidos. Ejemplo:")
        if raw:
            print(f"        {raw[0]}")
    except Exception as e:
        print(f"   [ERROR] -> {e}")
        return
        
    print(f"\n3. Testing Data Pipeline - get_enriched_data()...")
    try:
        df = client.get_enriched_data(experimento_id=EXP_ID, dias=7)
        print(f"   [OK] Pandas DataFrame generado. {len(df)} filas.")
        print("\n   [MUESTRA DE LA MATRIZ CIENTÍFICA (VPD CALCULADO)]")
        print(df[['timestamp', 'node_id', 'temperature', 'humidity', 'vpd_kpa', 'temp_ma_24h']].head())
    except Exception as e:
        print(f"   [ERROR] -> {e}")
        return

    print(f"\n4. Test de Denegación de Acceso (Llave incorrecta)...")
    try:
        bad_client = DemeterClient(api_key="HACKER-KEY-123", base_url=BASE_URL)
        bad_client.get_raw_data(experimento_id=EXP_ID, dias=1)
        print("   [ERROR CRITICO] Logramos acceder con llave inválida.")
    except Exception as e:
        print(f"   [OK] El servidor rechazó el acceso correctamente: {e}")

    print(f"\n5. Generando Suite Analítica Completa (CSV + Gráficas)...")
    try:
        output_path = client.run_full_suite(experimento_id=EXP_ID, dias=7, output_dir="./output_cientifico")
        print(f"   [OK] ¡Éxito! Puedes ver la matriz científica completa en formato CSV y las gráficas aquí: {output_path}")
    except Exception as e:
        print(f"   [ERROR] -> {e}")

    print("\n Test de Integración Local Superado!")
    
if __name__ == "__main__":
    main()
