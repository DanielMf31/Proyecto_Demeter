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
UartStrategy uartStrategy(&Serial2, 115200);

ProtocolEngine engine(&uartStrategy);
GpioController gpioController;
SystemContext systemCtx(engine, gpioController);

void setup() {
    // Debug Serial
    Serial.begin(115200);
    delay(1000);
    Serial.println("=== RECEPTOR DEMETER V2 (SYSTEM CONTEXT) ===");
    
    // Iniciar Serial2 manual para asegurar pines (UartStrategy usa el objeto pero a veces requiere begin explicito)
    // Asumimos que UartStrategy.begin() llama a _serial->begin().
    // Pero HardwareSerial::begin tiene argumentos variables en ESP32 (baud, config, rx, tx).
    // UartStrategy standard solo llama begin(baud).
    // Por seguridad en ESP32, configuramos Serial2 antes.
    Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);

    // Inicializar Componentes a través del Contexto
    // systemCtx.setup() inicializará el Controller y bindeará los callbacks
    systemCtx.setup();
    
    // UartStrategy begin
    uartStrategy.begin();

    Serial.println("[INFO] Sistema Iniciado. Esperando Comandos...");
}

void loop() {
    // Toda la lógica ocurre aquí dentro
    systemCtx.loop();

    // Pequeño delay para estabilidad RTOS
    delay(1);
    
    // (Opcional) Debug input para pruebas manuales si fuera necesario,
    // pero idealmente el SystemContext maneja todo.
}