import pytest
from unittest.mock import MagicMock
from ejemplo_clases import SensorTemperatura, SistemaRiego

# -----------------------------------------------------------------------------
# 1. FIXTURE con MOCK
# -----------------------------------------------------------------------------
# Objetivo: Crear un sistema de riego donde el sensor NO sea real.
# Usamos MagicMock para crear un objeto falso que finge ser SensorTemperatura.
# -----------------------------------------------------------------------------
@pytest.fixture
def sistema_mockeado():
    # 1. Crear el Mock
    sensor_falso = MagicMock(spec=SensorTemperatura)
    
    # 2. Inyectarlo en la clase a probar
    # Esto es "Dependency Injection" en acción
    sistema = SistemaRiego(sensor_falso)
    
    # 3. Devolvemos AMBOS para poder configurarlos en los tests
    return sistema, sensor_falso

# -----------------------------------------------------------------------------
# 2. MARKERS (@pytest.mark.lento)
# -----------------------------------------------------------------------------
# Este test usa la clase original (sin mock). Tarda 1 segundo.
# Lo marcamos como 'lento' para poder excluirlo si queremos.
# Ejecutar: `pytest -m "not lento"` para saltarlo.
# -----------------------------------------------------------------------------
@pytest.mark.lento
def test_sistema_real_es_lento():
    sensor_real = SensorTemperatura()
    sistema = SistemaRiego(sensor_real)
    assert sistema.decidir_riego(30) == "MODO_AHORRO"

# -----------------------------------------------------------------------------
# 3. MEZCLA TOTAL: Mock + Fixture + Parametrize
# -----------------------------------------------------------------------------
# Objetivo: Probar la lógica de 'decidir_riego' sin esperar 1 segundo por test.
# Controlamos qué devuelve el sensor falso para probar todos los caminos (if/else).
# -----------------------------------------------------------------------------
@pytest.mark.parametrize("temp_simulada, umbral, accion_esperada", [
    (30.0, 25.0, "ACTIVAR_RIEGO"), # 30 > 25 -> Riego
    (20.0, 25.0, "MODO_AHORRO"),   # 20 < 25 -> Ahorro
    (25.0, 25.0, "MODO_AHORRO"),   # 25 == 25 -> Ahorro (Borde)
])
def test_logica_riego_con_mock(sistema_mockeado, temp_simulada, umbral, accion_esperada):
    # Desempaquetamos la fixture
    sistema, sensor_falso = sistema_mockeado
    
    # --- CONFIGURAR EL MOCK (Arrange) ---
    # Le ordenamos al sensor falso: "Cuando te llamen a leer_hardware, devuelve X"
    sensor_falso.leer_hardware.return_value = temp_simulada
    
    # --- EJECUTAR (Act) ---
    resultado = sistema.decidir_riego(umbral)
    
    # --- VERIFICAR (Assert) ---
    assert resultado == accion_esperada
    
    # Verificación extra: Asegurar que el sistema SÍ llamó al sensor
    sensor_falso.leer_hardware.assert_called_once()
