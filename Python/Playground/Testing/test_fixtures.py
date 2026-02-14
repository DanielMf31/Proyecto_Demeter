import pytest

# -----------------------------------------------------------------------------
# CONCEPTO: Fixtures (@pytest.fixture)
# -----------------------------------------------------------------------------
# Sirve para: Preparar un "estado conocido" antes de cada test.
# Es el bloque "Arrange" (Preparar) reutilizable.
#
# Sintaxis:
# 1. Defines una función decorada con @pytest.fixture.
# 2. Esa función retorna (return) o entrega (yield) el objeto que necesitas (ej: base de datos, usuario).
# 3. En tus tests, pones el NOMBRE de la función como argumento. Pytest inyecta el valor automáticamente.
# -----------------------------------------------------------------------------

# Definimos la Fixture
@pytest.fixture
def usuario_admin():
    """Crea un usuario administrador ficticio para los tests."""
    # Setup: Lo que pasa antes del test
    print("\n[Fixture] Creando usuario admin...")
    data = {
        "id": 1,
        "username": "admin",
        "rol": "superadmin",
        "activo": True
    }
    return data # Esto es lo que recibirá el test

# Usamos la Fixture
def test_admin_tiene_permisos_totales(usuario_admin):
    # Fíjate que 'usuario_admin' llega lleno gracias a pytest
    assert usuario_admin["rol"] == "superadmin"
    assert usuario_admin["activo"] is True

def test_admin_id_es_uno(usuario_admin):
    # Reutilizamos la misma configuración sin copiar código
    assert usuario_admin["id"] == 1

# -----------------------------------------------------------------------------
# FIXTURE CON TEARDOWN (Limpieza)
# -----------------------------------------------------------------------------
@pytest.fixture
def base_de_datos_temporal():
    # SETUP
    print("\n[DB] Conectando a Base de Datos...")
    db = {"estado": "conectado", "datos": []}
    
    yield db  # <-- Pausa aquí y ejecuta el test
    
    # TEARDOWN (Se ejecuta DESPUÉS del test, pase o falle)
    print("\n[DB] Cerrando conexión y limpiando...")
    db["estado"] = "desconectado"

def test_insertar_dato_db(base_de_datos_temporal):
    # Aquí estamos en la fase del 'yield'
    assert base_de_datos_temporal["estado"] == "conectado"
    base_de_datos_temporal["datos"].append("dato 1")
    assert len(base_de_datos_temporal["datos"]) == 1
