/*
 * EJEMPLO 1: I/O Básico en C++ (Streams)
 * Compilación: g++ 01_IO_Basico.cpp -o demo_io
 */

#include <iostream> // Input/Output Stream
#include <string>   // Para usar std::string (cadenas de verdad)
#include <iomanip>  // Para manipular formato (std::setw, std::hex)

int main() {
    // ---------------------------------------------------------
    // 1. Salida Básica (cout)
    // ---------------------------------------------------------
    std::cout << "Hola Mundo!" << std::endl; 
    // Output: Hola Mundo! (y salto de línea)

    int edad = 30;
    double altura = 1.75;

    // Encadenamiento de operadores <<
    std::cout << "Edad: " << edad << " | Altura: " << altura << "m" << std::endl;
    // Output: Edad: 30 | Altura: 1.75m

    // ---------------------------------------------------------
    // 2. Formato Avanzado (iomanip)
    // ---------------------------------------------------------
    int pixel_rojo = 255;
    std::cout << "Valor en Hex: 0x" 
              << std::hex << std::uppercase << pixel_rojo << std::dec << std::endl;
    // Output: Valor en Hex: 0xFF

    // Tablas alineadas con std::setw (Set Width)
    std::cout << "\n--- Tabla de Sensores ---\n";
    std::cout << std::left << std::setw(15) << "SENSOR" 
              << std::right << std::setw(10) << "VALOR" << std::endl;
    std::cout << std::setw(15) << "Temperatura" << std::setw(10) << 23.5 << std::endl;
    std::cout << std::setw(15) << "Humedad"     << std::setw(10) << 60 << std::endl;
    /* Output:
    --- Tabla de Sensores ---
    SENSOR              VALOR
    Temperatura          23.5
    Humedad                60
    */

    // ---------------------------------------------------------
    // 3. Entrada Básica (cin)
    // ---------------------------------------------------------
    std::string nombre;
    int numero_favorito;

    std::cout << "\nEscribe tu nombre (sin espacios): ";
    // std::cin lee hasta el primer espacio en blanco
    // Input simulado: Daniel 7
    if (std::cin >> nombre) {
        std::cout << "Hola, " << nombre << "!" << std::endl;
        // Output: Hola, Daniel!
    }

    // ---------------------------------------------------------
    // 4. Errores (cerr) y Logs (clog)
    // ---------------------------------------------------------
    // std::cerr no tiene buffer (sale inmediato), ideal para errores críticos
    std::cerr << "[ERROR] Esto es un mensaje de error crítico" << std::endl;
    // Output (stderr): [ERROR] Esto es un mensaje de error crítico

    return 0;
}
