#ifndef MAQUINA_ESTADO_H
#define MAQUINA_ESTADO_H

#include <Arduino.h>
#include "Configuracion.h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"

class MaquinaEstado {
  private:
    // VARIABLES PRIVADAS
    int estadoActual;
    unsigned long ultimaVerificacion;
    unsigned long intervaloVerificacion;
    ProcesamientoDatos& procesador;
    EjecucionComandos& ejecutor;
    
    // MÉTODOS PRIVADOS - solo declaraciones
    bool hayComandosUART();
    bool hayComandosPendientes();
    void cambiarEstado(int nuevoEstado);
    void EstadoEspera();
    void EstadoEjecucion(int comandoActual, int numero_comandos, Comando* comandos_parsed);
    void EstadoRecibiendo(int destino[100][4], Comando struct_comandos_local_parsed[100]);
    void EstadoError();

  public:
    // CONSTANTES PÚBLICAS
    static const int ESTADO_ESPERA = 0;
    static const int ESTADO_EJECUCION = 1;
    static const int ESTADO_RECIBIENDO = 2;
    static const int ESTADO_ERROR = 3;

    // CONSTRUCTOR
    MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej);
    
    // MÉTODOS PÚBLICOS
    void actualizar();
    int getEstadoActual();
    String getNombreEstado();
    void setIntervaloVerificacion(unsigned long intervalo);
    void ActuacionMaquinaEstados(int estadoActual);
};

#endif