#pragma once

class MathUtils {
public:
    static int sumar(int a, int b) {
        return a + b;
    }

    static int restar(int a, int b) {
        return a - b;
    }
    
    // Ejemplo para probar lógica defensiva en C++
    static float dividir(float a, float b) {
        if (b == 0.0f) {
            return 0.0f; // Comportamiento definido en lugar de excepción (común en embedded)
        }
        return a / b;
    }
};
