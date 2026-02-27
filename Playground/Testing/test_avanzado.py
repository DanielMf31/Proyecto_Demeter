import pytest
from utils_texto import es_palindromo
from matematicas_simples import sumar

# -----------------------------------------------------------------------------
# CONCEPTO: Parametrización (@pytest.mark.parametrize)
# -----------------------------------------------------------------------------
# Sirve para: Ejecutar la MISMA función de test múltiples veces con diferentes datos.
# Evita copiar y pegar tests (test_caso_1, test_caso_2, etc).
#
# Sintaxis:
# @pytest.mark.parametrize("nombre_arg1, nombre_arg2", [
#     (valor1_a, valor2_a),  <- Caso 1
#     (valor1_b, valor2_b),  <- Caso 2
# ])
#
# Los nombres "nombre_arg1", etc. DEBEN coincidir con los argumentos de la función `def`.
# -----------------------------------------------------------------------------

@pytest.mark.parametrize("texto, esperado", [
    ("ana", True),      # Caso Happy Path: Palíndromo simple
    ("Radar", True),    # Caso Edge: Mayúsculas (la función debe limpiar)
    ("luz azul", True), # Caso Edge: Espacios
    ("hola", False),    # Caso Happy Path: No es palíndromo
    (12345, False),     # Caso Defensive: No es string, debe devolver False (no explotar)
    ("", True),         # Caso Borde: String vacío
])

def test_es_palindromo_casos(texto, esperado):
    # Aquí 'texto' y 'esperado' van tomando los valores de la lista de arriba, uno por uno.
    assert es_palindromo(texto) == esperado

@pytest.mark.parametrize("a, b, resultado", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])

def test_sumar_varios_casos(a, b, resultado):
    assert sumar(a, b) == resultado