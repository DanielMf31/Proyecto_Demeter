// ========================================
// ARCHIVO: ComunicacionUART.h
// RUTA: include\ComunicacionUART.h
// ========================================

#ifndef COMUNICACIONUART_H
#define COMUNICACIONUART_H

#include <Arduino.h>
#include <HardwareSerial.h>

class ComunicacionUART {
private:
    HardwareSerial* serialPort;
    int rxPin;
    int txPin;
    long baudRate;
    
public:
    ComunicacionUART(HardwareSerial* port = nullptr, int rx = 16, int tx = 17, long baud = 115200);
    
    // Inicialización
    void inicializar();
    void reinicializar(int rx, int tx, long baud);
    
    // Comunicación básica
    void enviar(const String& mensaje);
    void enviarRaw(const byte* datos, size_t longitud);
    String recibir();
    bool hayDatosDisponibles();
    void limpiarBuffer();
    
    // Getters
    HardwareSerial* getSerial() const { return serialPort; }
    int getBaudRate() const { return baudRate; }
    bool estaConectado() const { return serialPort != nullptr; }
    
    // Utilidades
    void enviarComando(int a, int b, int c, int d, int e);
    void enviarComandoArray(const int comando[5]);
    bool recibirComando(int comando[5]);
};

#endif