#include <Arduino.h>
#include "MaquinaEstado.h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"
#include "Configuracion.h"

/**
 * @file main.cpp
 * @brief Punto de entrada principal del sistema Demeter
 * 
 * Configura el hardware y ejecuta el loop principal de control
 * del sistema de riego automatizado.
 */

// ✅ DEFINIR el array aquí (solo una vez en todo el proyecto)
int pines_actuadores[10][4] = {{BOMBA_1, BOMBA_2, BOMBA_3, BOMBA_4}};

// Instancias globales
ProcesamientoDatos procesador;
EjecucionComandos ejecutor;
MaquinaEstado maquina(procesador, ejecutor);

int estado_actual_general = 0;

/**
 * @brief Función de configuración inicial
 * 
 * Inicializa periféricos, configura pines GPIO y establece
 * comunicación serial.
 */
void setup() {
    // Configurar pines de actuadores
    for(int i = 0; i < 4; i++) {
        pinMode(pines_actuadores[0][i], OUTPUT);
        digitalWrite(pines_actuadores[0][i], LOW); // Estado inicial OFF
    }
    
    // Inicializar comunicación serial
    Serial.begin(115200);
    Serial2.begin(115200);
  
    // Mensaje de confirmación
    Serial.println("ESP32 Lista - Esperando datos...");  
}

/**
 * @brief Loop principal del sistema
 * 
 * Ejecuta continuamente la máquina de estados que controla
 * el flujo de operación del sistema de riego.
 */
void loop() {
    estado_actual_general = maquina.getEstadoActual();
    maquina.ActuacionMaquinaEstados(estado_actual_general);
}