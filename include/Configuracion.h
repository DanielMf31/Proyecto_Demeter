#ifndef CONFIGURACION_H
#define CONFIGURACION_H

/**
 * @file Configuracion.h
 * @brief Configuración global y estructuras del sistema Demeter
 * 
 * Contiene las definiciones de estructuras de datos principales
 * y configuración de hardware para el sistema de riego automatizado.
 */

// Definir la estructura Comando
/**
 * @struct Comando
 * @brief Representa una acción ejecutable en el sistema
 * 
 * Estructura que define un comando completo para controlar
 * actuadores del sistema de riego con temporización precisa.
 */
struct Comando {
    int actuador;       ///< Tipo de actuador: 0=bombas, 1=válvulas
    int numero;         ///< Identificador del dispositivo específico
    int estado;         ///< Estado deseado: 0=OFF, 1=ON
    int duracion;       ///< Duración de activación en milisegundos
    bool activo;        ///< Indica si el comando está en ejecución
    unsigned long inicio; ///< Marca de tiempo cuando inició la ejecución
};

// Configuración de pines
const int FILAS_BOMBAS = 3;     ///< Número de filas en el array de bombas
const int COLUMNAS_BOMBAS = 4;  ///< Número de columnas en el array de bombas

// Actuadores
    static const int BOMBA_1 = 2;  ///< GPIO2 - Bomba sector 1
    static const int BOMBA_2 = 3;  ///< GPIO3 - Bomba sector 2  
    static const int BOMBA_3 = 4;  ///< GPIO4 - Bomba sector 3
    static const int BOMBA_4 = 5;  ///< GPIO5 - Bomba sector 4

int pines_bombas[10][4] = {{BOMBA_1, BOMBA_2, BOMBA_3, BOMBA_4}};

#endif