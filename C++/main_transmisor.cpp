/*
TRANSMISOR ESP32-S3 - Puerto COM9
VERSIÓN SIMPLIFICADA
*/

#include <Arduino.h>
#include "ComunicacionUART.h"
#include "ProtocoloComunicacion.h"

// Instancias
ComunicacionUART uart(&Serial2, 16, 17, 115200);
ProtocoloComunicacion protocolo(uart, true);

// Datos
int datosPrueba[5][5] = {
    {1, 1, 0, 1000, 0},
    {1, 2, 0, 2000, 0},
    {1, 3, 0, 3000, 0},
    {1, 4, 0, 4000, 0},
    {1, 5, 0, 5000, 0}
};

unsigned long ultimoEstado = 0;

void mostrarMenu() {
    Serial.println("\n=== TRANSMISOR ESP32-S3 (COM9) ===");
    Serial.println("Comandos:");
    Serial.println("  i - Iniciar protocolo");
    Serial.println("  t - Test (envia 101)");
    Serial.println("  1-5 - Enviar comando individual");
    Serial.println("  a - Enviar 5 comandos");
    Serial.println("  r - Resetear");
    Serial.println("  e - Mostrar estado");
    Serial.println("  h - Mostrar menu");
}

void procesarComando(char cmd) {
    switch (cmd) {
        case 'i':
            protocolo.iniciarProtocolo();
            break;
        case 't':
            uart.enviar("101 0 0 0 0");
            break;
        case '1':
            uart.enviarComando(1, 1, 0, 1000, 0);
            break;
        case '2':
            uart.enviarComando(1, 2, 0, 2000, 0);
            break;
        case '3':
            uart.enviarComando(1, 3, 0, 3000, 0);
            break;
        case '4':
            uart.enviarComando(1, 4, 0, 4000, 0);
            break;
        case '5':
            uart.enviarComando(1, 5, 0, 5000, 0);
            break;
        case 'a':
            for (int i = 0; i < 5; i++) {
                uart.enviarComandoArray(datosPrueba[i]);
                delay(50);
            }
            break;
        case 'r':
            protocolo.reset();
            uart.limpiarBuffer();
            break;
        case 'e':
            Serial.print("Estado: ");
            Serial.println(protocolo.getEstadoTexto());
            break;
        case 'h':
            mostrarMenu();
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("TRANSMISOR ESP32-S3 - COM9");
    uart.inicializar();
    protocolo.configurarDatosTransmision(datosPrueba);
    
    mostrarMenu();
}

void loop() {
    if (Serial.available()) {
        char cmd = Serial.read();
        if (cmd != '\n' && cmd != '\r') {
            procesarComando(cmd);
        }
    }
    
    protocolo.procesarComunicacionTransmisor();
    
    if (millis() - ultimoEstado > 10000) {
        ultimoEstado = millis();
        if (protocolo.getEstado() != ProtocoloComunicacion::ESTADO_INICIAL) {
            Serial.print("[Estado] ");
            Serial.println(protocolo.getEstadoTexto());
        }
    }
    
    delay(10);
}