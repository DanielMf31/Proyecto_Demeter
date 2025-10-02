#ifndef EJECUCIONCOMANDOS_H
#define EJECUCIONCOMANDOS_H
#include <Arduino.h>

class EjecucionComandos {
  private:
    // Variables internas que SOLO esta clase usa
    int** pines_bombas;  // Array 2D de pines
    int filas_bombas;
    int columnas_bombas;

    // Métodos internos que no se usan desde fuera
    void configurarPin(int actuador, int numero, int estado) {
        if (actuador >= 0 && actuador < filas_bombas && 
            numero >= 0 && numero < columnas_bombas) {
            digitalWrite(pines_bombas[actuador][numero], estado);
        }
    }

  public:
    // Constructor - inicializa variables
    EjecucionComandos(int** pines, int filas, int columnas) {
        pines_bombas = pines;
        filas_bombas = filas;
        columnas_bombas = columnas;
    }

    // Métodos principales que otros pueden usar
    void iniciarComando(int idx, Comando comandos[]) {
        if (idx >= 0 && idx < 10) {
            comandos[idx].activo = true;
            comandos[idx].inicio = millis();
            configurarPin(comandos[idx].actuador, comandos[idx].numero, comandos[idx].estado);
        }
    }

    void terminarComando(int idx, Comando comandos[]) {
        if (idx >= 0 && idx < 10) {
            comandos[idx].activo = false;
            configurarPin(comandos[idx].actuador, comandos[idx].numero, LOW);
        }
    }
    
    // Getter para información (opcional)
    bool estaActivo(int idx, Comando comandos[]) {
        if (idx >= 0 && idx < 10) {
            return comandos[idx].activo;
        }
        return false;
    }
};

#endif