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

def dividir(a, b):
    """Divide dos números."""
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b

def obtener_elemento(lista, indice):
    """Obtiene un elemento de una lista."""
    if indice < 0 or indice >= len(lista):
        return None
    return lista[indice]    
