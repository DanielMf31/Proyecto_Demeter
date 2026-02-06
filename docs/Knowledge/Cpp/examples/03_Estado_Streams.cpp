/*
 * EJEMPLO 3: El "Estado" de los Streams
 * Compilación: g++ 03_Estado_Streams.cpp -o demo_state
 */

#include <iostream>
#include <iomanip>

int main() {
    int numero = 255;

    std::cout << "--- 1. Estado Base ---\n";
    std::cout << "Valor: " << numero << "\n"; 
    // Output: 255

    std::cout << "\n--- 2. Manipuladores Persistentes ('Sticky') ---\n";
    // std::hex CAMBIA el estado del stream para siempre (hasta que lo cambies de nuevo)
    std::cout << std::hex; 
    std::cout << "Valor Hex: " << numero << "\n";
    // Output: ff
    
    std::cout << "Valor otra vez: " << numero << "\n"; 
    // Output: ff (¡Sigue en Hex! El stream recuerda el estado)

    // Volvemos a decimal manualmente
    std::cout << std::dec; 

    std::cout << "\n--- 3. Manipuladores Temporales ---\n";
    // std::setw (Set Width) solo afecta al SIGUIENTE dato.
    std::cout << std::setw(10) << "Dato1" << "Dato2\n";
    // Output: "     Dato1Dato2"
    // 'Dato2' se imprimió pegado porque setw(10) se gastó con 'Dato1'.

    std::cout << "\n--- 4. Estado de Bool (true/false) ---\n";
    bool encendido = true;
    std::cout << "Bool normal: " << encendido << "\n";
    // Output: 1

    std::cout << std::boolalpha; // Activamos modo texto
    std::cout << "Bool alpha: " << encendido << "\n";
    // Output: true

    return 0;
}
