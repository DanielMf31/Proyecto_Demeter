// ========================================
// ARCHIVO: ComunicacionUART.cpp
// RUTA: src\Compartidos\ComunicacionUART.cpp
// ========================================

#include "ComunicacionUART.h"

ComunicacionUART::ComunicacionUART(HardwareSerial* port, int rx, int tx, long baud)
    : serialPort(port), rxPin(rx), txPin(tx), baudRate(baud) {
}

void ComunicacionUART::inicializar() {
    if (serialPort == nullptr) {
        Serial.println("[UART] Error: Puerto serial no configurado");
        return;
    }
    
    serialPort->begin(baudRate, SERIAL_8N1, rxPin, txPin);
    delay(100);
    
    Serial.printf("[UART] Inicializado en pines RX:%d, TX:%d, Baud:%ld\n", 
                  rxPin, txPin, baudRate);
}

void ComunicacionUART::reinicializar(int rx, int tx, long baud) {
    rxPin = rx;
    txPin = tx;
    baudRate = baud;
    
    if (serialPort != nullptr) {
        serialPort->end();
        delay(100);
        inicializar();
    }
}

void ComunicacionUART::enviar(const String& mensaje) {
    if (serialPort == nullptr) return;
    
    serialPort->println(mensaje);
    delay(2); // Pequeña pausa para estabilidad
}

void ComunicacionUART::enviarRaw(const byte* datos, size_t longitud) {
    if (serialPort == nullptr) return;
    
    serialPort->write(datos, longitud);
    delay(1);
}

String ComunicacionUART::recibir() {
    if (serialPort == nullptr || !hayDatosDisponibles()) {
        return "";
    }
    
    String mensaje = serialPort->readStringUntil('\n');
    mensaje.trim();
    return mensaje;
}

bool ComunicacionUART::hayDatosDisponibles() {
    return serialPort != nullptr && serialPort->available() > 0;
}

void ComunicacionUART::limpiarBuffer() {
    if (serialPort == nullptr) return;
    
    while (serialPort->available()) {
        serialPort->read();
    }
}

void ComunicacionUART::enviarComando(int a, int b, int c, int d, int e) {
    String mensaje = String(a) + " " + String(b) + " " + 
                     String(c) + " " + String(d) + " " + 
                     String(e);
    enviar(mensaje);
}

void ComunicacionUART::enviarComandoArray(const int comando[5]) {
    enviarComando(comando[0], comando[1], comando[2], comando[3], comando[4]);
}

bool ComunicacionUART::recibirComando(int comando[5]) {
    String mensaje = recibir();
    if (mensaje.length() == 0) return false;
    
    // Parsear los 5 valores
    int valores[5] = {0};
    int index = 0;
    int start = 0;
    
    for (int i = 0; i <= mensaje.length(); i++) {
        if (mensaje[i] == ' ' || i == mensaje.length()) {
            if (start < i && index < 5) {
                String numeroStr = mensaje.substring(start, i);
                valores[index] = numeroStr.toInt();
                index++;
            }
            start = i + 1;
        }
    }
    
    if (index == 5) {
        for (int i = 0; i < 5; i++) {
            comando[i] = valores[i];
        }
        return true;
    }
    
    return false;
}