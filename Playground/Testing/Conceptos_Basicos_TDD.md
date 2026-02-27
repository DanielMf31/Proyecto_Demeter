# Conceptos Básicos de Testing y TDD con Pytest

## 1. ¿Qué es TDD (Test Driven Development)?

TDD es una filosofía de desarrollo donde **escribes el test antes que el código**.
El ciclo se llama **Red - Green - Refactor**:

1.  🔴 **Red (Rojo):** Escribes un test para una funcionalidad que aún no existe. Ejecutas el test y falla (obvio, no hay código).
2.  🟢 **Green (Verde):** Escribes el código *mínimo e indispensable* para que el test pase. No busques la perfección, solo que funcione.
3.  🔵 **Refactor (Refactorizar):** Ahora que tienes un test que te protege (asegura que funciona), mejoras el código (limpias nombres, optimizas) sin miedo a romper nada.

---

## 2. Anatomía de un Test (AAA)
Todo test bien escrito sigue el patrón **AAA**:

*   **Arrange (Preparar):** Configuras los datos iniciales (variables, objetos).
*   **Act (Actuar):** Ejecutas la función que quieres probar.
*   **Assert (Afirmar):** Verificas que el resultado obtenido es igual al esperado.

```python
def test_suma_ejemplo():
    # Arrange
    numero_a = 5
    numero_b = 10
    
    # Act
    resultado = sumar(numero_a, numero_b)
    
    # Assert
    assert resultado == 15
```

---

## 3. ¿Por qué Pytest?
Es el framework estándar moderno en Python.
*   **Simple:** Usa la palabra clave nativa `assert` de Python, no necesitas métodos raros como `self.assertEqual`.
*   **Autodescubrimiento:** Encuentra automáticamente todos los archivos que empiecen por `test_` y las funciones `test_`.
*   **Fixtures:** Una forma potente de preparar datos reutilizables (Arrange) para múltiples tests.

---

## 4. Ejemplos Prácticos en esta carpeta
He creado dos archivos para que practiques:
1.  `matematicas_simples.py`: Funciones básicas (Suma, Resta, Strings).
2.  `test_matematicas.py`: Los tests que verifican esas funciones.

### Cómo ejecutar los tests
Abre una terminal en esta carpeta y escribe:
```bash
pytest
```

---

## 5. Conceptos Avanzados que has preguntado

### Happy Path vs. Sad Path (Edge Cases)
*   **Happy Path:** El camino ideal. "Si sumo 2+2, da 4". Es lo primero que testeas.
*   **Sad Path / Edge Cases:** ¿Qué pasa si algo sale mal? "Si intento poner mayúsculas a un número, ¿explota?".
    *   En TDD, **debes** pensar en cómo quieres que falle tu código.
    *   `pytest.raises(Error)` sirve para decir: "Espero que esto falle. Si NO falla, el test falla".

### Defensive Programming (Programación Defensiva)
Es el arte de anticipar problemas en los inputs.
En el ejemplo de `inyectar_dato`:
```python
if diccionario is None:
    diccionario = {}
```
Esto se llama **Defensive Programming**. En lugar de dejar que el programa se rompa (crash) porque el usuario olvidó crear el diccionario, tu función es "amable" y lo arregla o maneja el caso vacío.
*   **Ventaja:** Código más robusto que aguanta errores del usuario.
*   **Desventaja:** A veces oculta errores (¿quizás el usuario *quería* que fallara si no había diccionario?).

### Tipos de Excepciones Comunes en Python
Cuando usas `pytest.raises(TipoDeError)`, necesitas saber qué error esperar. Aquí los más comunes:

1.  **`ValueError`**: El tipo de dato es correcto (ej: es un número), pero el valor no tiene sentido.
    *   *Ejemplo:* `math.sqrt(-1)` (No hay raíz de negativos), `int("hola")`.
2.  **`TypeError`**: El tipo de dato es incorrecto.
    *   *Ejemplo:* `3 + "hola"` (No puedes sumar numero y texto).
3.  **`ZeroDivisionError`**: Dividir por cero.
    *   *Ejemplo:* `10 / 0`.
4.  **`IndexError`**: Intentar acceder a una posición que no existe en una lista.
    *   *Ejemplo:* `lista = [1, 2]; lista[5]`.
5.  **`KeyError`**: Intentar acceder a una clave que no existe en un diccionario.
    *   *Ejemplo:* `dicc = {"a": 1}; dicc["b"]`.

---

## 6. Siguientes Pasos: Refactorización y Parametrización

Una vez que estás en **Verde** (Tests pasando), no has terminado. Faltan dos conceptos clave:

### A. Refactorización (Limpiar el Código)
Ahora que tienes tests que te cubren, puedes simplificar tu lógica.
*   *Ejemplo:* En `dividir`, Python ya lanza `ZeroDivisionError` nativamente. ¿Realmente necesitamos el `if b == 0: raise ValueError`?
    *   Si quitamos el `if`, el código es más limpio y el error es el estándar (`ZeroDivisionError`).
    *   ¡Pero ojo! Si cambiamos el comportamiento, debemos actualizar el test.

### B. Parametrización (Data Driven Testing)
En lugar de escribir 20 funciones `test_suma_1`, `test_suma_2`, usamos `@pytest.mark.parametrize` para correr el mismo test con muchos datos distintos.

```python
import pytest

@pytest.mark.parametrize("input_a, input_b, esperado", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])
def test_sumar_varios_casos(input_a, input_b, esperado):
    assert sumar(input_a, input_b) == esperado
```
Esto ejecuta 4 tests independientes. Es muy potente para probar bordes.

### C. Fixtures (Setup/Teardown)
Si muchos tests necesitan lo mismo (ej: conectar a una Base de Datos o crear un Objeto complejo), usamos `@pytest.fixture`.
```python
@pytest.fixture
def usuario_admin():
    return {"nombre": "Admin", "rol": "Superuser"}

def test_puedo_borrar(usuario_admin):
    # 'usuario_admin' se inyecta automáticamente ya listo
    assert usuario_admin["rol"] == "Superuser"
```

---

## 7. Otros Conceptos Importantes (El siguiente nivel)

Ya dominas lo básico (Tests, Asserts, Fixtures, Parametrización). Aquí tienes la lista de lo que sigue en tu aprendizaje:

1.  **Mocking (Simulación):**
    *   *¿Qué es?* Crear objetos falsos que imitan a los reales.
    *   *¿Para qué?* Para testear tu código sin conectar la Base de Datos real, o sin tener el sensor físico conectado (¡Vital en tu proyecto de IoT!).
    *   *Herramienta:* `unittest.mock` o `pytest-mock`.

2.  **Code Coverage (Cobertura):**
    *   *¿Qué es?* Una métrica que te dice qué porcentaje de tu código fue ejecutado por los tests.
    *   *¿Para qué?* Para saber si te olvidaste de testear algún `if` o `else`.
    *   *Herramienta:* `pytest-cov`.

3.  **Markers (Marcadores):**
    *   *¿Qué es?* Etiquetas para tus tests.
    *   *Ejemplo:* `@pytest.mark.slow` (para tests que tardan mucho), `@pytest.mark.hardware` (para los que requieren la placa).
    *   *Uso:* `pytest -m "not slow"` (Corre todo menos lo lento).

4.  **`conftest.py` (Fixtures Globales):**
    *   *¿Qué es?* Un archivo mágico. Si pones tus fixtures ahí, **todos** los archivos de test las ven automáticamente sin importarlas.
    *   *Uso:* Ideal para configurar cosas globales del proyecto.

5.  **Scopes de Fixture (Ámbito):**
    *   Por defecto, una fixture se crea y destruye en cada test (`scope='function'`).
    *   Puedes hacer que dure toda la sesión (`scope='session'`) para cosas pesadas como "Arrancar la Base de Datos" una sola vez al principio.




