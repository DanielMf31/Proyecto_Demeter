def transformar_a_diccionarios(array_arrays):
    """
    Convierte un array de arrays en una lista de diccionarios
    con formato: actuador, numero, estado, tiempo
    """
    lista_diccionarios = []
    
    for subarray in array_arrays:
        diccionario = {
            "actuador": subarray[0],
            "numero": subarray[1], 
            "estado": subarray[2],
            "tiempo": subarray[3]
        }
        lista_diccionarios.append(diccionario)
    
    return lista_diccionarios

# Tu array de arrays
mi_array = [[0, 0, 0, 0], [1, 1, 1, 1]]

# Transformar
resultado = transformar_a_diccionarios(mi_array)

# Ver el resultado
print(resultado)