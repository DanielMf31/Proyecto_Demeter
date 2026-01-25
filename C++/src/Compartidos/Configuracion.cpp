#include "Configuracion.h"

// Definición de la instancia global
Configuracion sistemaConfig(&Serial2);

Configuracion::Configuracion(HardwareSerial* uart, int rx, int tx) 
    : perifericosInicializados(false), tiempoInicioSistema(0), 
      uartPort(uart), rxPin(rx), txPin(tx) {
}

void Configuracion::inicializarGPIO() {
    pinMode(PIN_LED_STATUS, OUTPUT);
    digitalWrite(PIN_LED_STATUS, LOW);
    
    Serial.println("[CONFIG] GPIO inicializado");
}

void Configuracion::inicializarSistema() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("\n=== INICIALIZANDO SISTEMA ESP32-S3 ===");
    Serial.println("[CONFIG] Inicializando perifericos...");
    
    // Inicializar GPIO
    inicializarGPIO();
    
    // Inicializar UART
    if (uartPort != nullptr) {
        uartPort->begin(BAUDRATE_UART, SERIAL_8N1, rxPin, txPin);
        Serial.printf("[CONFIG] UART2 inicializado en pines RX:%d, TX:%d, Baudrate:%d\n", 
                      rxPin, txPin, BAUDRATE_UART);
    } else {
        Serial.println("[CONFIG] UART no configurado - usando Serial por defecto");
        uartPort = &Serial;
    }
    
    tiempoInicioSistema = millis();
    perifericosInicializados = true;
    
    // LED indicador
    digitalWrite(PIN_LED_STATUS, HIGH);
    delay(500);
    digitalWrite(PIN_LED_STATUS, LOW);
    
    Serial.println("[CONFIG] Sistema inicializado correctamente");
    Serial.println("========================================\n");
}

void Configuracion::enviarMensajeUART(const String& mensaje) {
    if (uartPort) {
        uartPort->println(mensaje);
        delay(10); // Pequeña pausa para estabilidad
    }
}

String Configuracion::leerMensajeUART() {
    if (uartPort && uartPort->available()) {
        String mensaje = uartPort->readStringUntil('\n');
        mensaje.trim();
        return mensaje;
    }
    return "";
}

bool Configuracion::hayDatosUART() {
    return uartPort && (uartPort->available() > 0);
}

void Configuracion::flushUART() {
    if (uartPort) {
        while (uartPort->available()) {
            uartPort->read();
        }
    }
}