# Guía: Punteros, Accesos y Estructuras (C vs C++)

**Referencia:** `examples/04_Punteros_y_Accesos.cpp`

## 1. Structs vs Classes

### En C (`struct`)
*   Es solo una **bolsa de variables**.
*   No tiene funciones dentro.
*   Todo es público (cualquiera lo rompe).

### En C++ (`class`)
*   Es un **ente vivo**. Tiene datos y funciones (`métodos`).
*   Tiene **privacidad** (`private`/`public`). Protege sus datos.
*   Dato curioso: En C++, `struct` es técnicamente una `class` donde todo es `public` por defecto. Pero por convención, usamos `struct` solo para datos simples (como `Config`).

---

## 2. El Duelo: Punto (`.`) vs Flecha (`->`)

Esta es la duda #1 de todos. La regla es simple: **¿Qué tienes en la mano?**

### Tienes el Objeto (`.`)
Si tienes la variable real ("La caja"), usas punto.
```cpp
Robot r1;
r1.encender();
```

### Tienes la Dirección (`->`)
Si tienes un puntero ("La etiqueta de dónde está la caja"), usas flecha.
La flecha hace dos cosas: **Viaja a la dirección** Y **accede**.
```cpp
Robot* ptr = &r1;
ptr->encender(); 
// Es azúcar sintáctico para: (*ptr).encender()
```

---

## 3. Punteros vs Referencias (¿Cuál es superior?)

### C++ Introduce: La Referencia (`&`)
C tenía punteros. Eran potentes pero peligrosos (podían ser NULL o apuntar a basura).
C++ creó la Referencia.

| Característica | Puntero (`Robot* p`) | Referencia (`Robot& r`) |
| :--- | :--- | :--- |
| **Sintaxis acceso** | `p->metodo()` | `r.metodo()` (¡Más limpio!) |
| **¿Puede ser NULL?** | Sí (`nullptr`) | **No** (Siempre apunta a algo) |
| **¿Reasignable?** | Sí (puede apuntar a otro) | **No** (Nace y muere fiel) |
| **Uso Ideal** | Listas enlazadas, cosas opcionales | Pasar objetos a funciones |

### Veredicto de Superioridad

1.  **Usa `.` (Objeto/Referencia) SIEMPRE que puedas.**
    *   Es más seguro. No hay segfaults por NULL.
    *   Sintaxis más limpia.

2.  **Usa `->` (Puntero) SOLO cuando:**
    *   El objeto es opcional (puede no existir).
    *   Estás manejando memoria dinámica pura (aunque deberías usar `unique_ptr`, que también usa `->`).
    *   Necesitas polimorfismo (Interfaces).
