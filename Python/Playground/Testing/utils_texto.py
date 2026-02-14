def es_palindromo(texto):
    """Devuelve True si el texto se lee igual al revés."""
    if not isinstance(texto, str):
        return False
    texto_limpio = texto.replace(" ", "").lower()
    return texto_limpio == texto_limpio[::-1]
