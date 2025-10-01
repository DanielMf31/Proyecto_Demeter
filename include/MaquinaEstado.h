#ifndef MAQUINA_ESTADO_H
#define MAQUINA_ESTADO_H
#include "Configuracion.h"
#include "EjecucionComandos.h"

class MaquinaEstado {
  private:
    // VARIABLES PRIVADAS - solo se usan dentro de esta clase
    int estadoActual;
    unsigned long ultimaVerificacion;
    unsigned long intervaloVerificacion;
    
    // MÉTODOS PRIVADOS - funciones internas
    bool hayComandosUART() {
        return (Serial2.available() > 0);
    }
    
    bool hayComandosPendientes(bool comandosActivos) {
        return comandosActivos;
    }

    void cambiarEstado(int nuevoEstado) {
        if (nuevoEstado != estadoActual) {
            Serial.print("Cambiando estado: ");
            Serial.print(estadoActual);
            Serial.print(" -> ");
            Serial.println(nuevoEstado);
            estadoActual = nuevoEstado;
        }
    }

  public:
    // CONSTANTES PÚBLICAS - para usar desde fuera
    static const int ESTADO_ESPERA = 0;
    static const int ESTADO_EJECUCION = 1;
    static const int ESTADO_RECIBIENDO = 2;
    static const int ESTADO_ERROR = 3;
    // CONSTRUCTOR - se ejecuta al crear el objeto
    MaquinaEstado() {
        estadoActual = ESTADO_ESPERA;
        ultimaVerificacion = 0;
        intervaloVerificacion = 100; // ms entre verificaciones
    }
    
    // MÉTODO PRINCIPAL - se llama desde loop()
    void actualizar(bool hayComandosActivos) {
        // Verificar solo cada cierto tiempo (no saturar)
        unsigned long ahora = millis();
        if (ahora - ultimaVerificacion < intervaloVerificacion) {
            return;
        }
        ultimaVerificacion = ahora;
        
        // LÓGICA DE ESTADOS CORREGIDA
        if (hayComandosUART()) {
            cambiarEstado(ESTADO_RECIBIENDO);
        } 
        else if (hayComandosPendientes(hayComandosActivos)) {
            cambiarEstado(ESTADO_EJECUCION);
        }
        else {
            cambiarEstado(ESTADO_ESPERA);
        }
    }
    
    // GETTERS - para obtener información desde fuera
    int getEstadoActual() {
        return estadoActual;
    }
    
    String getNombreEstado() {
        switch(estadoActual) {
            case ESTADO_ESPERA: return "ESPERA";
            case ESTADO_EJECUCION: return "EJECUCION"; 
            case ESTADO_RECIBIENDO: return "RECIBIENDO";
            case ESTADO_ERROR: return "ERROR";
            default: return "DESCONOCIDO";
        }
    }
    
    // SETTERS - para configurar desde fuera
    void setIntervaloVerificacion(unsigned long intervalo) {
        intervaloVerificacion = intervalo;
    }

    /* 
    * FEATURE: Acciones para cada Estado de MaquinaEstado
    *
    * PROGRESO:
    * 
    * (X) ESTADO_ESPERA: 
    * ESTADO_EJECUCION: Acciones implementadas 
    * (X) ESTADO_RECIBIENDO: 
    * 
    */

    // TODO: Optimizar este cálculo - está muy lento
    // FIXME: Hay condición de carrera aquí cuando se llama desde ISR
    // NOTE: Esto usa 2KB de RAM - considerar mover a PROGMEM
    // HACK: Solución temporal hasta que llegue el hardware nuevo
    // BUG: No funciona con valores negativos

    void ActuacionMaquinaEstados(estadoActual){
        switch(estadoActual){ //Recibe el estado Actual y actúa en consecuencia
            
            case ESTADO_ESPERA:

            case ESTADO_EJECUCION:
            // TODO: Implementar la carga de comandos
            // cargarComandos(comandos_unparsed, comandos_parsed)

            // Debe haber una confirmación de que el array tiene elementos distintos a 0 en alguna posicion
                if(comandoActual < numero_comandos && comandos[comandoActual].activo){
                    unsigned long ahora = millis();

                    if(ahora - comandos[comandoActual].inicio >= comandos[comandoActual].duracion){
                        terminarComando(comandoActual, comandos_parsed);
                        comandoActual++;
                    }

                    
                    if(comandoActual < numero_comandos){ // Me falta implementar numero_comandos en ProcesamientoDatos
                        iniciarComando(comandoActual,comandos_parsed);
                    } else {
                    cambiarEstado(ESTADO_ESPERA) //Una vez que se ha superado la longitud del array máxima entonces se pone en "Idle"
                    comandos_unparsed = {};
                    cargarComandos(comandos_unparsed, comandos_parsed); // Esta parte no está implementada adecuadamente, revisar.
                    }
                }

            case ESTADO_RECIBIENDO:
                // TODO: Implementar la lectura de UART y el procesamiento de datos.
                // LeerMensajesUART();
            default:

        }
    }
};





#endif