# Sintaxis Básica: C vs C++

**Objetivo:** Entender los cambios "estéticos" y funcionales básicos antes de entrar en Clases y Objetos.

## 1. Cabeceras (Headers)

En C++ eliminamos el `.h` y añadimos una `c` al principio para las librerías estándar de C.

| C | C++ |
| :--- | :--- |
| `#include <stdio.h>` | `#include <cstdio>` |
| `#include <stdlib.h>` | `#include <cstdlib>` |
| `#include <string.h>` | `#include <cstring>` |
| `#include <stdint.h>` | `#include <cstdint>` |
| (No existe) | `#include <iostream>` (Nueva I/O) |
| (No existe) | `#include <vector>` (Arrays dinámicos) |

## 2. Salida y Entrada (Adiós printf/scanf)

C++ usa `Streams` (Flujos). Son más seguros porque no necesitas `%d`, `%s`. El compilador sabe el tipo.

**C (Printf):**
```c
int edad = 25;
printf("Tengo %d años\n", edad); // Si pones %s, CRASH.
```

**C++ (Cout - "Character Out"):**
```cpp
int edad = 25;
// "<<" es el operador de inserción. Empujas datos hacia la salida.
std::cout << "Tengo " << edad << " años" << std::endl; // Type-safe automático.
```

## 3. Espacios de Nombres (Namespaces)

En C, si tienes dos funciones `init()`, chocan.
En C++, las metemos en "apellidos" llamados `namespace`.

```cpp
// Librería A
namespace Motor {
    void init() { ... }
}

// Librería B
namespace Sensor {
    void init() { ... }
}

// Uso
Motor::init();  // Llama a la del motor
Sensor::init(); // Llama a la del sensor
```

*Nota:* `std` es el namespace estándar. Por eso escribimos `std::cout`.

## 4. Sobrecarga de Funciones (Overloading)

En C, no puedes llamar igual a dos funciones.
*   `imprimir_int(int a)`
*   `imprimir_float(float a)`

En C++, si los argumentos son distintos, **pueden llamarse igual**.

```cpp
void imprimir(int a) { 
    std::cout << "Entero: " << a << std::endl; 
}
void imprimir(float a) { 
    std::cout << "Float: " << a << std::endl; 
}

// Uso
imprimir(10);   // Llama a la versión int
imprimir(5.5f); // Llama a la versión float
```

## 5. El tipo `bool`

*   **C:** Necesitas `<stdbool.h>` o usar `int` (0/1).
*   **C++:** Es un tipo nativo. `true` y `false` son palabras reservadas.

## 6. Variables donde quieras y `auto`

En C antiguo (C89), debías declarar variables al inicio de la función.
En C++, declaras justo antes de usar. Y puedes usar `auto` para que el compilador adivine el tipo (como en Python, pero estático).

```cpp
auto x = 10;    // El compilador sabe que x es int
auto y = 3.14;  // El compilador sabe que y es double
auto& motor = obtenerMotor(); // Sabe que es una Referencia a Motor
```

---

## Ejemplo Resumen (`main.cpp`)

```cpp
#include <iostream> // I/O C++
#include <cstdio>   // printf (compatible)

namespace Demo {
    void saludar(int veces) {
        for(int i=0; i<veces; i++) {
            std::cout << "Hola C++ " << i << std::endl;
        }
    }
}

int main() {
    auto numero = 3; // int
    
    // Podemos mezclar, pero cout es preferido
    printf("Inicio estilo C\n"); 
    
    Demo::saludar(numero);
    
    return 0;
}
```
