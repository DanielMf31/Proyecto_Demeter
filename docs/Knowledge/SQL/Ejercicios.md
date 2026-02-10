# Ejercicios de Entrenamiento 🏋️‍♂️

## Parte 1: SQL Puro (Usando "Execute SQL" en DB Browser)

Abre tu `playground.db` en DB Browser y vete a la pestaña "Ejecutar SQL". Intenta resolver estos retos:

### Ejercicio 1: El Limpiador
Hay sensores antiguos que ya no sirven.
*   **Objetivo**: Borra todos los sensores que sean de tipo "Humedad".
*   **Pista**: Usa `DELETE`.

### Ejercicio 2: El Corrector
El "Sensor Salón" se ha movido. Ahora está en el "Dormitorio".
*   **Objetivo**: Cambia el nombre del sensor "Sensor Salón" a "Sensor Dormitorio".
*   **Pista**: Usa `UPDATE`.

### Ejercicio 3: El Inspector
Queremos saber qué sensores están fallando (valores muy altos o muy bajos).
*   **Objetivo**: Selecciona todos los sensores cuyo valor sea mayor a 80 O menor a 10.
*   **Pista**: Usa `SELECT`, `WHERE`, `OR`.

---

## Parte 2: Python + SQL (Scripts)

Crea estos archivos en tu carpeta `Python/Playground/SQL/` y completa el código.

### Ejercicio 4: `ejercicio_input.py`
Crea un script que pida al usuario por consola los datos y los guarde.
1.  `input("Nombre: ")`
2.  `input("Tipo: ")`
3.  `input("Valor: ")`
4.  Hacer el `INSERT` usando `?` (Placeholders).

### Ejercicio 5: `ejercicio_contador.py`
Crea un script que cuente cuántos sensores hay de cada tipo.
1.  Pregunta al usuario: "¿Qué tipo quieres contar? (Temp/Humedad/etc)".
2.  Ejecuta un `SELECT` usando `COUNT` o lee todos y cuenta en Python.
3.  Imprime: "Hay X sensores de tipo Y".

### Ejercicio 6: `ejercicio_borrador_seguro.py`
Crea un script para borrar un sensor por su ID.
1.  Muestra todos los sensores (ID y Nombre) para que el usuario elija.
2.  Pide: "Introduce el ID a borrar: ".
3.  **Importante**: Pregunta "¿Estás seguro? (s/n)".
4.  Si dice 's', ejecuta el `DELETE`.
