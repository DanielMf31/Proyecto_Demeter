#ifndef CONFIGURACION_H
#define CONFIGURACION_H

#include <Arduino.h>
#include <HardwareSerial.h>

// ============================================
// CONSTANTES ESP32-S3
// ============================================

#define PIN_LED_STATUS 21
#define UART2_RX 16    // GPIO16 para RX
#define UART2_TX 17    // GPIO17 para TX
#define BAUDRATE_UART 115200

// ============================================
// CLASE CONFIGURACION
// ============================================

class Configuracion {
private:
    bool perifericosInicializados;
    uint32_t tiempoInicioSistema;
    HardwareSerial* uartPort;
    int rxPin;
    int txPin;
    
    void inicializarGPIO();
    
public:
    Configuracion(HardwareSerial* uart = nullptr, int rx = UART2_RX, int tx = UART2_TX);
    
    void inicializarSistema();
    
    // Métodos UART
    void enviarMensajeUART(const String& mensaje);
    String leerMensajeUART();
    bool hayDatosUART();
    void flushUART();
    HardwareSerial* getUARTPort() { return uartPort; }
    
    // Getters
    bool estaInicializado() const { return perifericosInicializados; }
    uint32_t getTiempoActivo() const { return millis() - tiempoInicioSistema; }
    
    // Métodos UART directos (para mantener compatibilidad)
    void enviar(const String& mensaje) { enviarMensajeUART(mensaje); }
    String recibir() { return leerMensajeUART(); }
    bool disponible() { return hayDatosUART(); }
    void limpiarBuffer() { flushUART(); }
    
    // Métodos de comando para compatibilidad
    void enviarComando(int a, int b, int c, int d, int e) {
        enviarMensajeUART(String(a) + " " + String(b) + " " + String(c) + " " + String(d) + " " + String(e));
    }
    
    bool recibirComando(int comando[5]) {
        String mensaje = leerMensajeUART();
        if (mensaje.length() == 0) return false;
        
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
};

#endif