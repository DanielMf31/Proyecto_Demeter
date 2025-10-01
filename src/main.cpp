#include <Arduino.h>
#include "MaquinaEstado_h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"
#include "Configuracion.h"

// Estructuras de datos

Comando comandos_parsed[10]; // Array de formato estructuras de Comandos
int comandos_unparsed[2][4] = {{0,1,1,72},{0,2,0,10}}; // Array de prueba de comandos recibidos por la Raspberry.
int numero_comandos = sizeof(comandos_unparsed)/sizeof(comandos_unparsed[0];)


// Variables de control

void setup(){
    for(int i=0;i<4;i++){
        pinMode(PinesHardware::pines_bombas[0][i], OUTPUT); // Configuraciones.h
    }
    
    Serial.begin(115200);
    Serial2.begin(115200);

    comando_actual = 0;
  
  // Mensaje de confirmación
  Serial.println("ESP32 Lista - Esperando datos...");  
}

void loop(){


  
}
  