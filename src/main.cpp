#include <Arduino.h>
#include "MaquinaEstado.h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"
#include "Configuracion.h"

ProcesamientoDatos procesador;
EjecucionComandos ejecutor;
MaquinaEstado maquina(procesador, ejecutor);

int estado_actual_general = 0;

int pines_bombas;

void setup(){
    for(int i=0;i<4;i++){
        pinMode(pines_bombas[0][i], OUTPUT); // Configuraciones.h
    }
    
    Serial.begin(115200);
    Serial2.begin(115200);
  
  // Mensaje de confirmación
  Serial.println("ESP32 Lista - Esperando datos...");  

  
}

void loop(){
  estado_actual_general = maquina.getEstadoActual();
  maquina.ActuacionMaquinaEstados(estado_actual_general);

  
}
  