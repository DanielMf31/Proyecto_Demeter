#include "EjecucionComandos.h"

// CONSTRUCTOR
EjecucionComandos::EjecucionComandos(int** pines, int filas, int columnas) {
    pines_bombas = pines;
    filas_bombas = filas;
    columnas_bombas = columnas;
}

// MÉTODO PRIVADO
void EjecucionComandos::configurarPin(int actuador, int numero, int estado) {
    if (actuador >= 0 && actuador < filas_bombas && 
        numero >= 0 && numero < columnas_bombas) {
        digitalWrite(pines_bombas[actuador][numero], estado);
    }
}

// MÉTODOS PÚBLICOS
void EjecucionComandos::iniciarComando(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        comandos[idx].activo = true;
        comandos[idx].inicio = millis();
        configurarPin(comandos[idx].actuador, comandos[idx].numero, comandos[idx].estado);
    }
}

void EjecucionComandos::terminarComando(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        comandos[idx].activo = false;
        configurarPin(comandos[idx].actuador, comandos[idx].numero, LOW);
    }
}

void EjecucionComandos::cargarComandos(int origen[10][4], Comando destino[], int num_comandos) {
    for(int i = 0; i < num_comandos && i < 10; i++) {
        destino[i].actuador = origen[i][0];
        destino[i].numero = origen[i][1];
        destino[i].estado = origen[i][2];
        destino[i].duracion = origen[i][3];
        destino[i].activo = false;
        destino[i].inicio = 0;
    }
}

bool EjecucionComandos::estaActivo(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        return comandos[idx].activo;
    }
    return false;
}
