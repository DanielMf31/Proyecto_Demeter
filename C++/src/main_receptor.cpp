/*
* RECEPTOR ESP32-S3 - Nueva Arquitectura V2
* Implementa Strategy Pattern + System Context
*/

#include <Arduino.h>
#include "communications/UartStrategy.h"
#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SystemContext.h"

// Define Hardware Serial for ESP32
// RX=16, TX=17 (Ajustar según hardware)
#define RXD2 16
#define TXD2 17

// Instancias Globales
// UartStrategy recibe: Puntero a Serial, BaudRate
// En ESP32 Serial2 se inicializa dentro de UartStrategy si así está diseñado, 
// o pasamos el objeto global Serial2.
// Revisando UartStrategy.h, el constructor es: UartStrategy(HardwareSerial* serial, unsigned long baud)
// Instancias Globales
// UartStrategy recibe: Puntero a Serial, BaudRate, RX Pin, TX Pin
UartStrategy uartStrategy(&Serial2, 115200, RXD2, TXD2);

ProtocolEngine engine(&uartStrategy);
GpioController gpioController;
SystemContext systemCtx(engine, gpioController);

void setup() {
    // Debug Serial
    Serial.begin(115200);
    delay(1000);
    while(!Serial) delay(10);

    Serial.println("=== DEMETER RECEPTOR V2 (MVP GPIO) ===");
    Serial.println(" [1-4] Toggle PIN 4-7");
    Serial.println(" [I] Modo Inmediato (Default)");
    Serial.println(" [R] Modo Recepción (Cola)");
    Serial.println(" [E] Ejecutar Cola");
    Serial.println(" [C] Limpiar Cola");
    Serial.println("======================================");

    // Initialize System
    systemCtx.setup();
    // UartStrategy.begin() now handles Serial2.begin(baud, config, rx, tx) internally
    uartStrategy.begin();
}

void loop() {
    // 1. System Loop (Protocol Engine)
    systemCtx.loop();

    // 2. User Interactive Menu (Serial USB)
    if (Serial.available()) {
        char c = toupper(Serial.read());
        // Simple state tracking for toggling
        static bool pinStates[8] = {false}; 

        switch (c) {
            case 'I':
                systemCtx.setExecutionMode(ExecutionMode::IMMEDIATE);
                Serial.println(">> MODO: INMEDIATO");
                break;
            case 'R':
                systemCtx.setExecutionMode(ExecutionMode::INTERACTIVE_QUEUE);
                Serial.println(">> MODO: RECEPCION (Encolando...)");
                break;
            case 'E':
                Serial.println(">> EJECUTANDO COLA...");
                systemCtx.executeQueue();
                break;
            case 'C':
                systemCtx.clearQueue();
                Serial.println(">> COLA LIMPIA");
                break;
            
            // Manual GPIO Control
            case '1':
            case '2':
            case '3':
            case '4': {
                uint8_t pin = (c - '0') + 3; // '1'->4, '2'->5, '3'->6, '4'->7
                pinStates[pin] = !pinStates[pin]; // Toggle
                
                Demeter::SetGpioCmd cmd;
                cmd.pin = pin;
                cmd.value = pinStates[pin];
                cmd.flags = 0;

                Serial.printf(">> MANUAL: PIN %d -> %s\n", pin, cmd.value ? "ON" : "OFF");
                systemCtx.injectCommand(cmd);
                break;
            }

            case '\n':
            case '\r':
                break;
            default:
                Serial.print("Comando desconocido: ");
                Serial.println(c);
                break;
        }
    }
}