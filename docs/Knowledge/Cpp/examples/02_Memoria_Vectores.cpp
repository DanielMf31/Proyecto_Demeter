/*
 * EJEMPLO 2: Memoria, Punteros y Vectores
 * Compilación: g++ 02_Memoria_Vectores.cpp -o demo_mem
 */

#include <iostream>
#include <vector>   // Array dinámico (lo usarás el 99% de las veces)
#include <memory>   // Smart Pointers (unique_ptr)

class Sensor {
public:
    int id;
    Sensor(int i) : id(i) { std::cout << "  [CTOR] Sensor " << id << " creado.\n"; }
    ~Sensor() { std::cout << "  [DTOR] Sensor " << id << " destruido.\n"; }
    
    void leer() { std::cout << "    -> Leyendo Sensor " << id << "...\n"; }
};

int main() {
    // ---------------------------------------------------------
    // 1. std::vector "El Array que crece solo"
    // ---------------------------------------------------------
    std::cout << "\n--- 1. std::vector ---\n";
    
    // Equivalente a declarar un array, pero sin tamaño fijo
    std::vector<int> datos;
    
    // Añadimos elementos dinámicamente
    datos.push_back(10);
    datos.push_back(20);
    datos.push_back(30);
    
    std::cout << "Tamaño actual: " << datos.size() << std::endl;
    // Output: Tamaño actual: 3
    
    // Acceso como array C
    std::cout << "Dato[1]: " << datos[1] << std::endl;
    // Output: Dato[1]: 20
    
    // Iteración moderna (Range-based for loop)
    // "Por cada 'valor' en 'datos'..."
    std::cout << "Contenido: ";
    for(int valor : datos) {
        std::cout << valor << " ";
    }
    std::cout << std::endl;
    // Output: Contenido: 10 20 30

    // ---------------------------------------------------------
    // 2. Punteros Inteligentes (Smart Pointers)
    // ---------------------------------------------------------
    std::cout << "\n--- 2. Smart Pointers (RAII) ---\n";
    
    {
        // Scope limitado para demostración
        std::cout << "Creando Puntero Inteligente...\n";
        
        // unique_ptr es el DUEÑO exclusivo. Reemplaza a 'new'.
        auto ptr = std::make_unique<Sensor>(99);
        // Output: [CTOR] Sensor 99 creado.
        
        ptr->leer();
        // Output: -> Leyendo Sensor 99...
        
        std::cout << "Saliendo del bloque...\n";
    } // <-- AQUÍ ptr muere automáticamente. No hay delete.
    // Output: [DTOR] Sensor 99 destruido.
    
    std::cout << "Bloque finalizado. Memoria limpia.\n";

    // ---------------------------------------------------------
    // 3. Referencias vs Punteros Crudos
    // ---------------------------------------------------------
    std::cout << "\n--- 3. Referencias ---\n";
    
    int variable = 100;
    int& alias = variable; // 'alias' ES 'variable' con otro nombre.
    
    alias = 200; // Modificamos alias
    std::cout << "Variable original: " << variable << std::endl;
    // Output: Variable original: 200 (¡Cambió!)
    
    return 0;
}
