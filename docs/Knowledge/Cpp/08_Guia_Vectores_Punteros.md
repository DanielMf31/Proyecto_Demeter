# Guía: Vectores y Memoria en C++

**Referencia:** Código de ejemplo `examples/02_Memoria_Vectores.cpp`

## 1. `std::vector` (El adiós a los arrays fijos)

En C, tenías que adivinar el tamaño: `int datos[100];`. ¿Y si necesitas 101? Mala suerte (buffer overflow).
En C++, usamos `std::vector`.

*   **Dinámico:** Crece solo (`push_back`).
*   **Seguro:** Sabe cuánto mide (`.size()`).
*   **Limpio:** Se libera solo al salir de la función (RAII).

```cpp
std::vector<int> lista;
lista.push_back(5); // [5]
lista.push_back(10); // [5, 10]
lista.size(); // Devuelve 2
```

## 2. Punteros Inteligentes (`std::unique_ptr`)

Como vimos en la guía de Memoria, en C++ moderno **evitamos `new` y `delete` manuales**.
Usamos `std::unique_ptr`.

*   **Propiedad Exclusiva:** Solo un puntero puede poseer el objeto.
*   **Autolimpieza:** Cuando el puntero sale de ámbito (`}`), hace `delete` automáticamente.

## 3. Punteros Crudos (`*`) vs Referencias (`&`)

| Característica | Puntero (`*`) | Referencia (`&`) |
| :--- | :--- | :--- |
| **¿Puede ser NULL?** | SÍ (`nullptr`) | **NO** (Siempre apunta a algo válido) |
| **¿Reasignable?** | SÍ (puede apuntar a otro lado) | **NO** (Nace y muere atada a su variable) |
| **Uso Principal** | Estructuras de datos complejas, C legacy | Pasar objetos a funciones sin copiar |

**Regla de Oro en Demeter:**
Usa **Referencias (`&`)** siempre que puedas (argumentos de función).
Usa **Punteros (`*`)** solo si el objeto puede no existir (ser opcional/null).
