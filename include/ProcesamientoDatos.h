#ifndef PROCESAMIENTODATOS_H
#define PROCESAMIENTODATOS_H

#include <Arduino.h>
#include "Configuracion.h"

// Forward declaration para tests
class TestProcesamientoDatos;

class ProcesamientoDatos{
  private:
    // Variables internas
    int valores[4];
    int comandoCount;
    Comando comandos_parsed[10];
    int comandos_unparsed[2][4];
    int numero_comandos;
    int ComandoActual;
 
    // Declaraciones de métodos PRIVADOS
    void procesarMensaje(String mensajeRecibido, int destino[100][4]);
    void cargarComandos(int origen[10][4], Comando destino[]);

  public:
    // Constructor
    ProcesamientoDatos();
    
    
    /**
     * @brief 
     * 
     * @param destino 
     */
    void LeerMensajesUART(int destino[100][4]);

    // Getters
    Comando* getComandosParsed();
    int (*getComandosUnparsed())[4];
    int getComandoCount();
    int getComandoActual();
    int getNumeroComandos();

    // Setters
    void incrementarComandoActual();
    void resetArrayComandos();
    
    // ✅ Friend class para tests
    friend class TestProcesamientoDatos;
};

#endif