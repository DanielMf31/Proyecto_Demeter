#include "MaquinaEstado.h"
#include "ProcesamientoDatos.h"

// CONSTRUCTOR
MaquinaEstado::MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej) 
    : procesador(proc), ejecutor(ej) {
    estadoActual = ESTADO_ESPERA;
    ultimaVerificacion = 0;
    intervaloVerificacion = 100;
}

// MÉTODOS PRIVADOS

// Getters 
bool MaquinaEstado::hayComandosUART() {
    return (Serial2.available() > 0);
}

bool MaquinaEstado::hayComandosPendientes() {
}


void MaquinaEstado::cambiarEstado(int nuevoEstado) {
    if (nuevoEstado != estadoActual) {
        Serial.print("Cambiando estado: ");
        Serial.print(estadoActual);
        Serial.print(" -> ");
        Serial.println(nuevoEstado);
        estadoActual = nuevoEstado;
    }
}

// MÉTODOS PÚBLICOS

void MaquinaEstado::EstadoEspera(){}
void MaquinaEstado::EstadoEjecucion(int comandoActual, int numero_comandos, Comando* comandos_parsed){
    if(comandoActual < numero_comandos && comandos_parsed[comandoActual].activo) {
                unsigned long ahora = millis();

                if(ahora - comandos_parsed[comandoActual].inicio >= comandos_parsed[comandoActual].duracion) {
                    ejecutor.terminarComando(comandoActual, comandos_parsed);
                    procesador.incrementarComandoActual();
                    comandoActual = procesador.getComandoActual();
                }

                if(comandoActual < numero_comandos) {
                    ejecutor.iniciarComando(comandoActual, comandos_parsed);
                } else {
                    cambiarEstado(ESTADO_ESPERA);
                    procesador.resetArrayComandos();
                    // procesador.cargarComandos(comandos_unparsed, comandos_parsed);
                }
            }
}
void MaquinaEstado::EstadoError(){}
void MaquinaEstado::EstadoRecibiendo(int destino[100][4], Comando struct_comandos_local_parsed[100]){
    procesador.LeerMensajesUART(destino);
    procesador.cargarComandos(destino, struct_comandos_local_parsed);
            
}

void MaquinaEstado::actualizar() {
    unsigned long ahora = millis();
    if (ahora - ultimaVerificacion < intervaloVerificacion) {
        return;
    }
    ultimaVerificacion = ahora;
    
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

int MaquinaEstado::getEstadoActual() {
    return estadoActual;
}

String MaquinaEstado::getNombreEstado() {
    switch(estadoActual) {
        case ESTADO_ESPERA: return "ESPERA";
        case ESTADO_EJECUCION: return "EJECUCION"; 
        case ESTADO_RECIBIENDO: return "RECIBIENDO";
        case ESTADO_ERROR: return "ERROR";
        default: return "DESCONOCIDO";
    }
}

//Setters

void MaquinaEstado::setIntervaloVerificacion(unsigned long intervalo) {
    intervaloVerificacion = intervalo;
}

void MaquinaEstado::ActuacionMaquinaEstados(int estadoActual) {
    int comandoActual = procesador.getComandoActual();
    int numero_comandos = procesador.getNumeroComandos();
    int array_comandos_local_unparsed[100][4];
    Comando struct_comandos_local_parsed[100];

    procesador.getComandosUnparsed(array_comandos_local_unparsed);
    
    
    switch(estadoActual) {
        case ESTADO_ESPERA:
            break;

        case ESTADO_EJECUCION:
            EstadoEjecucion(comandoActual, numero_comandos, struct_comandos_local_parsed);
            break;

        case ESTADO_RECIBIENDO:
           EstadoRecibiendo(array_comandos_local_unparsed, struct_comandos_local_parsed);

        default:                                
            break;
    }
}