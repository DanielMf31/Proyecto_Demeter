def sumar(a, b):
    """Suma dos números."""
    return a + b

def restar(a, b):
    """Resta dos números."""
    return a - b

def poner_en_mayusculas(texto):
    """Convierte un texto a mayúsculas. Lanza error si no es texto."""
    if not isinstance(texto, str):
        raise ValueError("El input debe ser un string")
    return texto.upper()

def inyectar_dato(diccionario, clave, valor):
    """Injecta una clave-valor en un diccionario existente."""
    if diccionario is None:
        diccionario = {}
    diccionario[clave] = valor
    return diccionario

def calcular_descuento(precio, descuento):
    """Calcula el precio con descuento."""
    if descuento < 0 or descuento > 100:
        raise ValueError("El descuento debe estar entre 0 y 100")
    return precio * (1 - descuento / 100)