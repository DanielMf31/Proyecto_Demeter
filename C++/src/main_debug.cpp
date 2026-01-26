/*
 DEBUG PROGRAM - PROYECTO DEMETER
 PROPOSITO: Verificar subida de código y RECEPCIÓN DE DATOS (Input).
 FUNCION: Menú interactivo controlado por Serial.
*/

#include <Arduino.h>

const int pines[] = {4, 5, 6, 7};
const int numPines = 4;

void mostrarMenu() {
    Serial.println("\n\n=== MENU DEBUG ===");
    Serial.println("1 - Ejecutar Secuencia LEDs (4-7)");
    Serial.println("2 - Prueba de Eco (Escribe algo y pulsa enter)");
    Serial.println("h - Mostrar este menu");
    Serial.println("Escribe tu opcion y pulsa ENTER:");
}

void secuenciaLeds() {
    Serial.println(">> Iniciando secuencia de LEDs...");
    for(int i=0; i<numPines; i++) {
        digitalWrite(pines[i], HIGH);
        Serial.printf("   ON  Pin %d\n", pines[i]);
        delay(500);
        digitalWrite(pines[i], LOW);
        Serial.printf("   OFF Pin %d\n", pines[i]);
    }
    Serial.println(">> Secuencia terminada.");
}

void setup() {
    Serial.begin(115200);
    // Configurar pines
    for(int i=0; i<numPines; i++) {
        pinMode(pines[i], OUTPUT);
        digitalWrite(pines[i], LOW);
    }
    
    delay(2000); // Espera inicial
    Serial.println("SISTEMA ARRANCADO");
    mostrarMenu();
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim(); // Quitar espacios/saltos de linea
        
        if (input.length() > 0) {
            Serial.print("Recibido: [");
            Serial.print(input);
            Serial.println("]");

            char opcion = input.charAt(0);
            
            switch(opcion) {
                case '1':
                    secuenciaLeds();
                    break;
                case '2':
                    Serial.println(">> OK! El puerto serie funciona en AMBAS direcciones.");
                    break;
                case 'h':
                    mostrarMenu();
                    break;
                default:
                    Serial.println(">> Opcion no reconocida. Escribe 'h' para ayuda.");
                    break;
            }
        }
    }
    delay(10);
}
