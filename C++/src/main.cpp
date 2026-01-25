/*
RECEPTOR ESP32-S3 - Puerto COM10
VERSIÓN SIMPLIFICADA - SIN MÁQUINA DE ESTADOS COMPLEJA
*/

#include <Arduino.h>
#include "ComunicacionUART.h"
#include "ProtocoloComunicacion.h"
#include "EjecucionComandos.h"

// Instancias
ComunicacionUART uart(&Serial2, 16, 17, 115200);
ProtocoloComunicacion protocolo(uart, false);
EjecucionComandos ejecutor;

// Variables de control
bool autoEjecutar = false;
int comandosGuardados = 0;
int comandoActual = 0;
bool ejecutando = false;
unsigned long tiempoInicioComando = 0;

// Estados simples
enum Estado { ESPERA, RECIBIENDO, EJECUTANDO };
Estado estado = ESPERA;

void mostrarMenu() {
    Serial.println("\n=== RECEPTOR ESP32-S3 (COM10) ===");
    Serial.println("Comandos:");
    Serial.println("  r - Recibir datos (espera transmisor)");
    Serial.println("  e - Ejecutar TODOS los comandos");
    Serial.println("  s - Detener ejecucion");
    Serial.println("  d - Mostrar estado y comandos");
    Serial.println("  x - Resetear todo");
    Serial.println("  c - Limpiar comandos");
    Serial.println("  p - Probar actuadores");
    Serial.println("  1-5 - Activar actuador manual (1s)");
    Serial.println("  h - Mostrar este menu");
}

void mostrarEstado() {
    Serial.println("\n=== ESTADO ACTUAL ===");
    Serial.print("Estado: ");
    switch(estado) {
        case ESPERA: Serial.println("ESPERA"); break;
        case RECIBIENDO: Serial.println("RECIBIENDO"); break;
        case EJECUTANDO: Serial.println("EJECUTANDO"); break;
    }
    
    Serial.print("Comandos guardados: ");
    Serial.println(ejecutor.getComandoCount());
    
    if (estado == EJECUTANDO) {
        Serial.print("Comando actual: ");
        Serial.println(comandoActual + 1);
        Serial.print("Total: ");
        Serial.println(ejecutor.getComandoCount());
    }
    
    Serial.print("Auto-ejecucion: ");
    Serial.println(autoEjecutar ? "ON" : "OFF");
    Serial.println("=====================");
}

void procesarComando(char cmd) {
    switch (cmd) {
        case 'r':
            if (estado != ESPERA) {
                Serial.println("Error: Ya está en modo recepción o ejecución");
                return;
            }
            Serial.println("Escuchando transmisor...");
            estado = RECIBIENDO;
            break;
            
        case 'e':
            if (estado != ESPERA) {
                Serial.println("Error: Ya está ejecutando o recibiendo");
                return;
            }
            if (ejecutor.getComandoCount() == 0) {
                Serial.println("Error: No hay comandos para ejecutar");
                return;
            }
            Serial.print("Ejecutando ");
            Serial.print(ejecutor.getComandoCount());
            Serial.println(" comandos...");
            estado = EJECUTANDO;
            comandoActual = 0;
            ejecutando = false;
            break;
            
        case 's':
            Serial.println("Deteniendo ejecucion...");
            estado = ESPERA;
            ejecutor.detenerTodosLosComandos();
            ejecutando = false;
            break;
            
        case 'd':
            mostrarEstado();
            ejecutor.mostrarComandosLocales();
            break;
            
        case 'x':
            Serial.println("Reseteando todo...");
            estado = ESPERA;
            protocolo.reset();
            uart.limpiarBuffer();
            ejecutor.limpiarComandos();
            ejecutando = false;
            comandosGuardados = 0;
            Serial.println("Sistema reseteado");
            break;
            
        case 'c':
            Serial.println("Limpiando comandos...");
            ejecutor.limpiarComandos();
            comandosGuardados = 0;
            break;
            
        case 'p':
            Serial.println("Probando actuadores...");
            ejecutor.pruebaActuadores();
            break;
            
        case '1':
            Serial.println("A1 manual por 1s");
            ejecutor.anadirComando(1, 1, 0, 1000, 0);
            break;
        case '2':
            Serial.println("A2 manual por 1s");
            ejecutor.anadirComando(1, 2, 0, 1000, 0);
            break;
        case '3':
            Serial.println("A3 manual por 1s");
            ejecutor.anadirComando(1, 3, 0, 1000, 0);
            break;
        case '4':
            Serial.println("A4 manual por 1s");
            ejecutor.anadirComando(1, 4, 0, 1000, 0);
            break;
        case '5':
            Serial.println("A5 manual por 1s");
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

void procesarEjecucion() {
    if (!ejecutando) {
        // Iniciar nuevo comando
        ejecutor.ejecutarComando(comandoActual);
        ejecutando = true;
        tiempoInicioComando = millis();
    } else {
        // Verificar si el comando actual terminó
        if (ejecutor.haCompletadoDuracion(comandoActual)) {
            ejecutor.detenerComando(comandoActual);
            comandoActual++;
            ejecutando = false;
            
            if (comandoActual >= ejecutor.getComandoCount()) {
                // Todos los comandos ejecutados
                Serial.println("\n✓ TODOS los comandos ejecutados");
                estado = ESPERA;
                ejecutando = false;
            } else {
                Serial.print("→ Siguiente comando: ");
                Serial.println(comandoActual + 1);
            }
        }
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println("RECEPTOR ESP32-S3 - COM10");
    Serial.println("Sistema Invernadero Automático");
    Serial.println("===============================");
    
    uart.inicializar();
    mostrarMenu();
}

void loop() {
    // 1. Leer comandos del usuario
    if (Serial.available()) {
        char cmd = Serial.read();
        if (cmd != '\n' && cmd != '\r') {
            procesarComando(cmd);
        }
    }
    
    // 2. Procesar protocolo de comunicación
    protocolo.procesarComunicacionReceptor();
    
    // 3. Verificar si recibimos datos
    if (estado == RECIBIENDO && protocolo.getEstado() == ProtocoloComunicacion::COMUNICACION_COMPLETADA) {
        int comandosRecibidos = protocolo.getComandoCount();
        
        if (comandosRecibidos > 0) {
            // Obtener los comandos del protocolo
            int comandosBuffer[100][5];
            protocolo.getComandos(comandosBuffer);
            
            // Cargarlos al ejecutor
            ejecutor.cargarComandosDesdeArray(comandosBuffer, comandosRecibidos);
            
            Serial.print("✓ Recibidos ");
            Serial.print(comandosRecibidos);
            Serial.println(" comandos");
            
            // Resetear protocolo para nueva recepción
            protocolo.reset();
            estado = ESPERA;
            
            // Auto-ejecutar si está activado
            if (autoEjecutar) {
                Serial.println("Auto-ejecutando...");
                estado = EJECUTANDO;
                comandoActual = 0;
                ejecutando = false;
            }
        }
    }
    
    // 4. Ejecutar comandos si estamos en modo ejecución
    if (estado == EJECUTANDO) {
        procesarEjecucion();
    }
    
    // 5. Verificar completados en ejecutor (por si acaso)
    ejecutor.verificarCompletados();
    
    delay(10);
}