#ifndef EJECUCIONCOMANDOS_H
#define EJECUCIONCOMANDOS_H

#include <Arduino.h>

class EjecucionComandos {
private:
    int comandosLocales[100][5];
    int comandoCount;
    bool comandoActivo[100];
    unsigned long tiemposInicio[100];
    
    // Pines fijos - sin conflictos
    static const int PIN_A1 = 4;
    static const int PIN_A2 = 5;
    static const int PIN_A3 = 6;
    static const int PIN_A4 = 7;
    static const int PIN_A5 = 8;
    
    int pinParaActuador(int numeroActuador);
    void configurarPin(int numeroActuador, int estado);
    
public:
    EjecucionComandos();
    
    // Métodos principales
    void cargarComandosDesdeArray(int comandosExternos[100][5], int count);
    void ejecutarComando(int idx);
    void detenerComando(int idx);
    void detenerTodosLosComandos();
    
    // Métodos de verificación
    bool estaActivo(int idx);
    bool haCompletadoDuracion(int idx);
    void verificarCompletados();
    
    // Métodos de información
    int getComandoCount() const { return comandoCount; }
    void mostrarComandosLocales();
    void pruebaActuadores();
    
    // Método para limpiar comandos
    void limpiarComandos();
    
    // Método para añadir comandos individuales (CORREGIDO: sin ñ)
    void anadirComando(int tipo, int actuador, int parametro, int duracion, int reservado);
    
    // Getter para pines
    static int getPinForActuador(int actuador) {
        switch(actuador) {
            case 1: return PIN_A1;
            case 2: return PIN_A2;
            case 3: return PIN_A3;
            case 4: return PIN_A4;
            case 5: return PIN_A5;
            default: return -1;
        }
    }
};

#endif