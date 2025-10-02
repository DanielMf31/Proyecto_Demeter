#ifndef MAQUINA_ESTADO_H
#define MAQUINA_ESTADO_H

#include <Arduino.h>
#include "Configuracion.h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"



class MaquinaEstado {
  private:
    // VARIABLES PRIVADAS - solo se usan dentro de esta clase
    int estadoActual;
    unsigned long ultimaVerificacion;
    unsigned long intervaloVerificacion;

    ProcesamientoDatos& procesador; // Referencia a la instancia procesador
    EjecucionComandos& ejecutor;


    
    // MÉTODOS PRIVADOS - funciones internas
    bool hayComandosUART() {
        return (Serial2.available() > 0);
    }
    
    bool hayComandosPendientes(bool comandosActivos) {
        return procesador.hayComandosActivos();
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
    MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej) : procesador(proc), ejecutor(ej) {
        estadoActual = ESTADO_ESPERA;
        ultimaVerificacion = 0;
        intervaloVerificacion = 100; // ms entre verificaciones
    }
    
    // MÉTODO PRINCIPAL - se llama desde loop()
    void actualizar() {
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
        else if (hayComandosPendientes()) {
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

    void ActuacionMaquinaEstados(int getEstadoActual()){

        int comandoActual = procesador.getComandoActual();
        int numero_comandos = procesador.getNumeroComandos();
        Comando* comandos_parsed = procesador.getComandosParsed();


        switch(estadoActual){ //Recibe el estado Actual y actúa en consecuencia
            
            case ESTADO_ESPERA:

            case ESTADO_EJECUCION:
            // TODO: Implementar la carga de comandos
            // cargarComandos(comandos_unparsed, comandos_parsed)

            // Debe haber una confirmación de que el array tiene elementos distintos a 0 en alguna posicion
                if(comandoActual < numero_comandos && comandos_parsed[comandoActual].activo){
                    unsigned long ahora = millis();

                    if(ahora - comandos_parsed[comandoActual].inicio >= comandos_parsed[comandoActual].duracion){
                        ejecutor.terminarComando(comandoActual, comandos_parsed);
                        procesador.incrementarComandoActual();
                        comandoActual = procesador.getComandoActual();
                    }

                    
                    if(comandoActual < numero_comandos){ // Me falta implementar numero_comandos en ProcesamientoDatos
                        ejecutor.iniciarComando(comandoActual,comandos_parsed);
                    } else {
                    cambiarEstado(ESTADO_ESPERA); //Una vez que se ha superado la longitud del array máxima entonces se pone en "Idle"
                    procesador.resetArrayComandos();
                    procesador.cargarComandos(comandos_unparsed, comandos_parsed); // Esta parte no está implementada adecuadamente, revisar.
                    }
                }

            case ESTADO_RECIBIENDO:
                // TODO: Implementar la lectura de UART y el procesamiento de datos.
                procesador.LeerMensajesUART(); // Debe apuntar al comandos_unparsed de ProcesamientoDatos
            default:

        }
    }
};





#endif