#ifndef PROCESAMIENTODATOS_H
#define PROCESAMIENTODATOS_H

#include <Arduino.h>
#include "Configuracion.h"

class TestProcesamientoDatos;

class ProcesamientoDatos{
  private:
    int valores[4];
    int comandoCount;
    Comando comandos_parsed[10];
    int comandos_unparsed[100][4];
    int numero_comandos;
    int ComandoActual;

    void procesarMensaje(String mensajeRecibido, int destino[100][4]);
    

  public:
    ProcesamientoDatos();
    
    void LeerMensajesUART(int destino[100][4]);

    // Getters CORREGIDO
    void getComandosUnparsed(int destino[100][4]);   // Copia a array proporcionado
    int getComandoCount();
    int getComandoActual();
    int getNumeroComandos();

    // Para obtener un comando unparsed específico
    void cargarComandos(int origen[100][4], Comando destino[100]);

    void incrementarComandoActual();
    void resetArrayComandos();
    
    friend class TestProcesamientoDatos;
};

#endif