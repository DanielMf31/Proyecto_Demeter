#ifndef CONFIGURACION_H
#define CONFIGURACION_H

// Definir la estructura Comando

struct Comando {
    int actuador;
    int numero;
    int estado;
    int duracion;
    bool activo;
    unsigned long inicio;
};

// Configuración de pines
const int FILAS_BOMBAS = 3;
const int COLUMNAS_BOMBAS = 4;

struct PinesHardware{

    //Sensores

    // Actuadores

    static const int BOMBA_1 = 2;
    static const int BOMBA_2 = 3;
    static const int BOMBA_3 = 4;
    static const int BOMBA_4 = 5;

    int pines_bombas[10][4] = {{BOMBA_1,BOMBA_2,BOMBA_3,BOMBA_4}}; //Bombas 1,2,3 y 4

    // Comunicacion
};

#endif