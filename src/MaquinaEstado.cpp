#include "MaquinaEstado.h"

// CONSTRUCTOR
MaquinaEstado::MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej) 
    : procesador(proc), ejecutor(ej) {
    estadoActual = ESTADO_ESPERA;
    ultimaVerificacion = 0;
    intervaloVerificacion = 100;
}

// MÉTODOS PRIVADOS
bool MaquinaEstado::hayComandosUART() {
    return (Serial2.available() > 0);
}

bool MaquinaEstado::hayComandosPendientes() {
    return procesador.hayComandosActivos();
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

void MaquinaEstado::setIntervaloVerificacion(unsigned long intervalo) {
    intervaloVerificacion = intervalo;
}

void MaquinaEstado::ActuacionMaquinaEstados(int estadoActual) {
    int comandoActual = procesador.getComandoActual();
    int numero_comandos = procesador.getNumeroComandos();
    Comando* comandos_parsed = procesador.getComandosParsed();

    switch(estadoActual) {
        case ESTADO_ESPERA:
            // Código para estado espera
            break;

        case ESTADO_EJECUCION:
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
            break;

        case ESTADO_RECIBIENDO:
            // procesador.LeerMensajesUART();
            break;

        default:
            break;
    }
}