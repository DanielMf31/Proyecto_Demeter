import pytest
from matematicas_simples import sumar, restar, poner_en_mayusculas, inyectar_dato

# 1. Tests Básicos (Happy Path)
def test_sumar_numeros_positivos():
    # Arrange -> Act -> Assert (en una línea)
    assert sumar(2, 3) == 5

def test_restar_numeros():
    assert restar(10, 4) == 6

# 2. Test de Manejo de Strings
def test_string_a_mayusculas():
    entrada = "hola mundo"
    resultado = poner_en_mayusculas(entrada)
    assert resultado == "HOLA MUNDO"

# 3. Test de Estructuras de Datos (Diccionarios)
def test_inyectar_datos_en_diccionario():
    # Arrange
    mi_diccionario = {"nombre": "Daniel"}
    clave_nueva = "rol"
    valor_nuevo = "Admin"
    
    # Act
    resultado = inyectar_dato(mi_diccionario, clave_nueva, valor_nuevo)
    
    # Assert
    assert resultado["nombre"] == "Daniel" # Lo viejo sigue ahí
    assert resultado["rol"] == "Admin"     # Lo nuevo se añadió
    assert len(resultado) == 2

# 4. Test de Errores (Edge Cases)
def test_mayusculas_lanza_error_con_numeros():
    # Verificamos que al pasar un número, la función "se queje" (lance error)
    with pytest.raises(ValueError):
        poner_en_mayusculas(123)

    # Si pasamos None, debería devolver un diccionario nuevo con el dato
    resultado = inyectar_dato(None, "clave", "valor")
    assert isinstance(resultado, dict)
    assert resultado["clave"] == "valor"

# 5. TDD: Nueva funcionalidad (Fase RED)
# Queremos una funcion que calcule descuentos
from matematicas_simples import calcular_descuento

def test_calcular_descuento_basico():
    # Precio 100, Descuento 20% -> Pagar 80
    assert calcular_descuento(100, 20) == 80.0

def test_descuento_invalido_lanza_error():
    # No existen descuentos negativos (Programación Defensiva)
    with pytest.raises(ValueError):
        calcular_descuento(100, -10)

# 6. TDD RETO: Divisiones y Listas (Fase RED)
from matematicas_simples import dividir, obtener_elemento

def test_dividir_numeros():
    assert dividir(10, 2) == 5.0
    assert dividir(7, 2) == 3.5

def test_dividir_por_cero_error():
    # Queremos que lance ZeroDivisionError
    with pytest.raises(ZeroDivisionError):
        dividir(10, 0)

def test_obtener_elemento_lista_seguro():
    lista = ["a", "b", "c"]
    assert obtener_elemento(lista, 1) == "b"

def test_obtener_elemento_indice_invalido():
    # Si pedimos un índice que no existe, ¿qué quieres que pase?
    # OPCIÓN A: Que lance IndexError (Standard)
    # OPCIÓN B: Que devuelva None ("Defensive") <<-- Vamos a probar esta lógica defensiva
    lista = ["a", "b"]
    assert obtener_elemento(lista, 99) is None
