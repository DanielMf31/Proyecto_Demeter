/*
RECEPTOR ESP32-S3 - Puerto COM10
VERSIÓN SIMPLIFICADA Y FUNCIONAL
*/

#include <Arduino.h>
#include "ComunicacionUART.h"
#include "ProtocoloComunicacion.h"
#include "EjecucionComandos.h"
#include "MaquinaEstado.h"

// Instancias
ComunicacionUART uart(&Serial2, 16, 17, 115200);
ProtocoloComunicacion protocolo(uart, false);
EjecucionComandos ejecutor;
MaquinaEstado maquina(protocolo, ejecutor);

// Variables
bool autoEjecutar = false;

void mostrarMenu() {
    Serial.println("\n=== RECEPTOR ESP32-S3 (COM10) ===");
    Serial.println("Comandos:");
    Serial.println("  r - Recibir datos del transmisor");
    Serial.println("  e - Ejecutar TODOS los comandos");
    Serial.println("  s - Detener ejecucion");
    Serial.println("  d - Mostrar estado");
    Serial.println("  x - Resetear todo");
    Serial.println("  c - Limpiar comandos");
    Serial.println("  p - Probar actuadores");
    Serial.println("  1-5 - Activar actuador manual");
    Serial.println("  h - Mostrar este menu");
}

void procesarComando(char cmd) {
    switch (cmd) {
        case 'r':
            maquina.iniciarRecepcion();
            break;
        case 'e':
            maquina.iniciarEjecucion();
            break;
        case 's':
            maquina.detenerEjecucion();
            break;
        case 'd':
            Serial.print("Estado: ");
            Serial.println(maquina.getEstadoTexto());
            Serial.print("Comandos: ");
            Serial.println(ejecutor.getComandoCount());
            break;
        case 'x':
            maquina.resetear();
            protocolo.reset();
            uart.limpiarBuffer();
            ejecutor.limpiarComandos();
            Serial.println("Sistema reseteado");
            break;
        case 'c':
            ejecutor.limpiarComandos();
            Serial.println("Comandos limpiados");
            break;
        case 'p':
            ejecutor.pruebaActuadores();
            break;
        case '1':
            ejecutor.anadirComando(1, 1, 0, 1000, 0);
            break;
        case '2':
            ejecutor.anadirComando(1, 2, 0, 1000, 0);
            break;
        case '3':
            ejecutor.anadirComando(1, 3, 0, 1000, 0);
            break;
        case '4':
            ejecutor.anadirComando(1, 4, 0, 1000, 0);
            break;
        case '5':
            ejecutor.anadirComando(1, 5, 0, 1000, 0);
            break;
        case 'h':
            mostrarMenu();
            break;
        default:
            Serial.print("Comando desconocido: ");
            Serial.println(cmd);
            break;
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("RECEPTOR ESP32-S3 - COM10");
    uart.inicializar();
    maquina.inicializar();
    // Serial.println(">> Maquina/Protocolo DESACTIVADOS para prueba");
    
    mostrarMenu();
}

void loop() {
    if (Serial.available()) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        
        Serial.print("DEBUG INPUT: [");
        Serial.print(input);
        Serial.println("]");
        
        if (input.length() > 0) {
            char cmd = input.charAt(0);
            procesarComando(cmd);
        }
    }
    
    protocolo.procesarComunicacionReceptor();
    maquina.actualizar();
    
    // Solo verificar completados externos si la máquina NO está controlando la ejecución
    // Esto evita condiciones de carrera donde el ejecutor detiene el comando antes que la máquina se entere
    if (maquina.getEstadoCompleto().estadoMaquina != 3) { // 3 = ESTADO_EJECUTANDO
        ejecutor.verificarCompletados();
    }
    
    delay(10);
}