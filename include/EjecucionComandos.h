#ifndef EJECUCIONCOMANDOS_H
#define EJECUCIONCOMANDOS_H

#include <Arduino.h>
#include "Configuracion.h"

class EjecucionComandos {
  private:
    // Variables internas que SOLO esta clase usa
    int** pines_bombas;  // Array 2D de pines
    int filas_bombas;
    int columnas_bombas;

    // Métodos internos que no se usan desde fuera
    void configurarPin(int actuador, int numero, int estado);

  public:
    // Constructor - inicializa variables
    EjecucionComandos(int** pines, int filas, int columnas);

    // Métodos principales que otros pueden usar
    void iniciarComando(int idx, Comando comandos[]);
    void terminarComando(int idx, Comando comandos[]);
    void cargarComandos(int origen[10][4], Comando destino[], int num_comandos);

    // Getter para información (opcional)
    bool estaActivo(int idx, Comando comandos[]);
};

#endif