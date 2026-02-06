# Gestión de Memoria: C vs C++

**Objetivo:** Entender "quién limpia la basura" en cada lenguaje y ver cómo C++ automatiza lo que en C era manual y peligroso.

---

## 1. El Concepto Universal: Stack vs Heap

Esto aplica a AMBOS (C y C++).

### La Pila (Stack) - "Memoria Rápida y Automática"
Es donde viven las variables locales. Se crea al entrar a la función y muere al salir.
```c
void funcion() {
    int a = 10; // Creado en Stack
    // ... uso a ...
} // 'a' desaparece automáticamente aquí. Costo de limpieza: 0.
```

### El Montón (Heap) - "Memoria Manual y Persistente"
Es memoria que pides al sistema. Vive hasta que TÚ la liberes.
*   **Peligro:** Si olvidas liberarla -> *Memory Leak*.
*   **Peligro:** Si la liberas dos veces -> *Double Free* (Crash).

---

## 2. El Estilo C: manual hasta la muerte

En C, pides bytes crudos con `malloc` y devuelves bytes con `free`. `malloc` NO sabe qué estás guardando, solo sabe de tamaños.

```c
// C Code
typedef struct {
    int id;
    char buffer[100];
} Sensor;

void ejemplo_c() {
    printf("Inicio\n");

    // 1. Pedir memoria (Heap)
    // Tienes que calcular el tamaño manualmente.
    Sensor* s = (Sensor*)malloc(sizeof(Sensor)); 
    // Output: (Sistema busca hueco, devuelve puntero, basura dentro)
    
    // 2. Inicializar (Manual)
    s->id = 1; // Si olvidas esto, id es basura random
    printf("Sensor creado ID: %d\n", s->id);

    // 3. Usar
    // ...

    // 4. Liberar (CRÍTICO)
    free(s); // Si olvidas esto, esos bytes se pierden para siempre.
    printf("Memoria liberada\n");
}
```

---

## 3. El Estilo C++: Constructores y Destructores (RAII)

C++ introduce un concepto revolucionario: **La memoria va atada a la vida del objeto**.

*   Al crear (`new` o Stack): Se ejecuta el **Constructor** (Inicializa).
*   Al morir (`delete` o salir del scope): Se ejecuta el **Destructor** (Limpia).

```cpp
// C++ Code
class SensorCpp {
public:
    int id;
    
    // CONSTRUCTOR: Se ejecuta AUTOMÁTICAMENTE al crear
    SensorCpp(int nuevo_id) { 
        id = nuevo_id;
        std::cout << "[CTOR] Sensor " << id << " naciendo." << std::endl;
    }

    // DESTRUCTOR: Se ejecuta AUTOMÁTICAMENTE al morir
    ~SensorCpp() {
        std::cout << "[DTOR] Sensor " << id << " muriendo. Adiós mundo." << std::endl;
    }
};

void ejemplo_cpp_moderno() {
    std::cout << "--- Inicio Función ---" << std::endl;

    {
        // Variable en STACK.
        // Se crea aquí el objeto.
        SensorCpp s1(10); 
        // Output: [CTOR] Sensor 10 naciendo.
        
        std::cout << "Usando sensor..." << std::endl;
    } // <--- AQUÍ s1 SALE DE ÁMBITO (Scope)
      // C++ invoca AUTOMÁTICAMENTE a ~SensorCpp()
      // Output: [DTOR] Sensor 10 muriendo. Adiós mundo.

    std::cout << "--- Fin Función ---" << std::endl;
}
```

**Diferencia Clave:** En C++ **no escribí código para liberar**. El cierre de llave `}` disparó la limpieza. Esto se llama **RAII** (Resource Acquisition Is Initialization).

---

## 4. Modern C++: Smart Pointers (Olvídate de `new` y `delete`)

En C++ moderno (el que usas en el proyecto), evitamos usar `new` y `delete` manuales. Usamos "Punteros Inteligentes" que son dueños de la memoria Heap.

### `std::unique_ptr`
Es un puntero que dice: "Yo soy el ÚNICO dueño de este objeto. Cuando yo muera, el objeto muere".

```cpp
#include <memory>

void ejemplo_smart_pointer() {
    // malloc + constructor en uno. No usas 'new'.
    std::unique_ptr<SensorCpp> ptr = std::make_unique<SensorCpp>(55);
    // Output: [CTOR] Sensor 55 naciendo.

    // Lo usas igual que un puntero normal
    std::cout << "ID: " << ptr->id << std::endl;

    // NO HAY FREE. NO HAY DELETE.
} // <--- 'ptr' sale de ámbito.
  // Su destructor interno hace 'delete' de la memoria Heap automáticamente.
  // Output: [DTOR] Sensor 55 muriendo. Adiós mundo.
```

## Resumen

| Característica | C (`malloc`/`free`) | C++ (`new`/`delete`) | C++ Moderno (`unique_ptr`) |
| :--- | :--- | :--- | :--- |
| **Inicialización** | Manual (basura por defecto) | Automática (Constructor) | Automática (Constructor) |
| **Limpieza** | Manual (`free`) | Manual (`delete`) | **Automática** (al salir de scope) |
| **Seguridad** | Baja (Leaks, Double Free) | Media (Leaks si olvidas delete) | **Alta** (Imposible olvidar) |

**En tu proyecto Demeter:** Usamos RAII en `UartStrategy` y `ProtocolEngine`. No verás `malloc` manual. Si necesitas un buffer dinámico, usamos `std::vector` (que por dentro es un wrapper RAII de un array dinámico).
