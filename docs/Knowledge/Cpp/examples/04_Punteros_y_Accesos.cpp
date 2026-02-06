/*
 * EJEMPLO 4: Punteros, Referencias y el operador flecha (->)
 * Compilación: g++ 04_Punteros_y_Accesos.cpp -o demo_ptr
 */

#include <iostream>
#include <string>

// ---------------------------------------------------------
// 1. C-Style Struct (Datos tontos)
// ---------------------------------------------------------
struct DatosC {
    int valor;
};

// ---------------------------------------------------------
// 2. C++ Class (Datos + Métodos)
// ---------------------------------------------------------
class Robot {
public: // API Pública
    std::string nombre;

    void saludar() {
        std::cout << "Soy " << nombre << "!" << std::endl;
    }
};

int main() {
    // =========================================================
    // CASO A: Objetos en el Stack (Memoria Automática)
    // Usamos el PUNTO (.)
    // =========================================================
    std::cout << "--- A. Stack (Uso de Punto) ---\n";
    
    Robot r1;        // Instancia real, aquí mismo.
    r1.nombre = "R2D2";
    r1.saludar();    // Acceso directo.
    // r1 NO puede ser NULL. Siempre existe.

    // =========================================================
    // CASO B: Punteros (Direcciones de Memoria)
    // Usamos la FLECHA (->)
    // =========================================================
    std::cout << "\n--- B. Punteros (Uso de Flecha) ---\n";

    Robot* puntero = &r1; // 'puntero' guarda la dirección de r1 (ej: 0x7ffd...)
    
    // Forma FEA (Desreferenciar y luego punto): (*puntero).nombre
    // Forma ELEGANTE (Flecha):
    puntero->nombre = "C3PO"; // Modifica al original r1
    puntero->saludar();
    
    // La flecha significa: "Ve a esa dirección Y LUEGO accede al miembro"

    // =========================================================
    // CASO C: Referencias (La mejora de C++)
    // Usamos el PUNTO (.) pero por dentro es un puntero seguro
    // =========================================================
    std::cout << "\n--- C. Referencias (Lo mejor de ambos) ---\n";

    Robot& ref = r1; // Alias. No ocupa memoria extra (casi).
    
    ref.nombre = "BB-8"; // Sintaxis de punto (Fácil)
    ref.saludar();       // Efecto de puntero (Modifica original)

    // =========================================================
    // RESUMEN VISUAL
    // =========================================================
    // Objeto    (r1)      -> Usa .
    // Puntero   (*ptr)    -> Usa ->
    // Referencia (&ref)   -> Usa .
    
    return 0;
}
