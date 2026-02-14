# Testing en C++ con Unity (PlatformIO)

En el mundo de sistemas embebidos (Arduino/PlatformIO), el framework estándar no es `pytest`, sino **Unity**. Es ligero, está escrito en C y funciona tanto en tu PC (Native) como en el chip (Embedded).

## 1. La Sintaxis Básica (Asserts)

A diferencia de Python donde usas `assert a == b`, en Unity usas macros específicas para cada tipo de dato. Esto es crucial en C++ para que el test sepa cómo imprimir el error.

| Pytest (Python) | Unity (C/C++) | Descripción |
| :--- | :--- | :--- |
| `assert a == b` | `TEST_ASSERT_EQUAL_INT(a, b)` | Compara enteros (int). |
| `assert a == b` | `TEST_ASSERT_EQUAL_FLOAT(a, b)` | Compara flotantes. |
| `assert a == b` | `TEST_ASSERT_EQUAL_STRING(a, b)` | Compara cadenas de texto (char*). |
| `assert x is True` | `TEST_ASSERT_TRUE(x)` | Verifica booleanos verdaderos. |
| `assert x is False` | `TEST_ASSERT_FALSE(x)` | Verifica booleanos falsos. |
| `fail("Mensaje")` | `TEST_FAIL_MESSAGE("Mensaje")` | Fuerza el fallo del test. |

### Ejemplo de Estructura de un Archivo de Test (`test_main.cpp`)

```cpp
#include <unity.h>

// 1. Setup y Teardown (Fixtures)
void setUp(void) {
    // Se ejecuta ANTES de cada test (Ideal para reiniciar variables/objetos)
}

void tearDown(void) {
    // Se ejecuta DESPUÉS de cada test (Limpieza)
}

// 2. Los Tests
void test_led_builtin_pin_number(void) {
    TEST_ASSERT_EQUAL(2, LED_BUILTIN);
}

void test_suma_enteros(void) {
    TEST_ASSERT_EQUAL_INT(5, 2 + 3);
}

// 3. El Main (Runner)
int main(void) {
    UNITY_BEGIN(); // Inicia el framework

    RUN_TEST(test_led_builtin_pin_number);
    RUN_TEST(test_suma_enteros);

    return UNITY_END(); // Termina y reporta resultados
}
```

---

## 2. Conceptos Avanzados en C++

### A. Fixtures (`setUp` / `tearDown`)
En Python usábamos `@pytest.fixture`. En Unity, estas funciones son **globales** por archivo.
*   `setUp()`: Es el constructor de tu entorno. Reinicia tus objetos aquí.
*   `tearDown()`: Es el destructor. Libera memoria (`delete`) aquí si usaste `new`.

### B. Mocking (El reto de C++)
C++ no es dinámico como Python. No puedes "parchear" una función mágicamente.
Para hacer Mocks en C++, usamos **Interfaces (Clases Abstractas Puras)** y **Inyección de Dependencias (DI)**.

**Ejemplo Conceptual:**
```cpp
// 1. La Interfaz (Contrato)
class ISensor {
    public: virtual float leer() = 0;
};

// 2. El Mock (Tu clase falsa para tests)
class MockSensor : public ISensor {
    public:
        float valorSimulado = 25.0; // Controlable desde el test
        
        float leer() override {
            return valorSimulado; 
        }
};

// 3. El Test
void test_riego_se_activa_con_calor() {
    MockSensor sensorFalso;
    sensorFalso.valorSimulado = 40.0; // Simulamos calor extremo
    
    ControladorRiego riego(&sensorFalso); // Inyección de Dependencia
    
    TEST_ASSERT_TRUE(riego.debeRegar());
}
```
Esto es lo que hemos estado haciendo con `IComms` y `ProtocolEngine`.

### C. Parametrización
Unity no tiene `@parametrize`. Tienes que hacerlo "a mano" con un bucle o función helper.

```cpp
void helper_test_suma(int a, int b, int esperado) {
    TEST_ASSERT_EQUAL_INT(esperado, a + b);
}

void test_suma_parametrizada() {
    helper_test_suma(2, 3, 5);
    helper_test_suma(0, 0, 0);
    helper_test_suma(-1, 1, 0);
}
```

---

## 3. Siguientes Pasos (Nivel Intermedio)

### A. Native vs. Embedded Testing
PlatformIO te permite correr los tests en dos sitios:
1.  **Native (`env:native`):** Compila con GCC en tu Linux/PC.
    *   *Ventaja:* Ultrarápido (milisegundos). Ideal para lógica pura (`ProtocolEngine`, matemáticas, parsers).
    *   *Desventaja:* No tiene Arduino.h ni hardware real. Tienes que mockear `Serial`, `WiFi`, etc.
2.  **Embedded (`env:sensor`):** Compila cruzado y sube al ESP32.
    *   *Ventaja:* Prueba el hardware real (GPIOs, Timers, WiFi).
    *   *Desventaja:* Lento (tienes que flashear).

### B. Mocks vs. Fakes (Dobles de Prueba)
Manual de supervivencia cuando no tienes la librería `unittest.mock` de Python:
1.  **Fake:** Una clase real pero simplificada.
    *   *Ej:* `FakeEEPROM` que guarda los datos en un `std::vector` en RAM en lugar de la flash.
    *   *Uso:* Bueno para probar estados.
2.  **Mock:** Una clase que verifica *comportamiento*.
    *   *Ej:* "Verifica que se llamó a `send()` exactamente 3 veces".
    *   *En C++:* A menudo lo implementamos a mano guardando contadores (`callCount++`) en la clase falsa.

---

## 4. Hardware Abstraction Layer (HAL)
Para testear código de Arduino en PC (`native`), necesitas separar el hardware.
*   **Mal:** `digitalWrite(13, HIGH);` dentro de tu lógica.
*   **Bien:** `_io->setPin(13, HIGH);` donde `_io` es una interfaz.
    *   En `native`, `_io` es un Mock que imprime "Encendiendo pin 13".
    *   En `embedded`, `_io` llama al `digitalWrite` real.

---

## 5. Troubleshooting (Errores Comunes)

### Error: `undefined reference to 'setUp'`
*   **Causa:** Unity espera `setUp()` y `tearDown()`. Si no los usas, defínelos vacíos.

### Error: `was not declared in this scope` en `RUN_TEST`
*   **Causa:** Tienes `RUN_TEST(mi_test)` en el `main`, pero olvidaste definir la función `void mi_test(void)` o la borraste por error.
*   **Solución:** Asegúrate que cada test listado en `main` existe.

### Error: `Does not name a type` en archivos `src/`
*   **Causa:** Al correr tests `native`, PlatformIO compila todo `src/`. Si tienes un archivo `Node_Actuator.cpp` que no incluye su propio `.h`, fallará aquí aunque no lo uses en el test.
*   **Solución:** Todos los `.cpp` en `src/` deben incluir sus headers correspondientes (`#include "MiClase.h"`).


