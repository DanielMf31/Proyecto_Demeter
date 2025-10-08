#ifndef EJECUCIONCOMANDOS_H
#define EJECUCIONCOMANDOS_H

#include <Arduino.h>
#include "Configuracion.h"

/**
 * @file EjecucionComandos.h
 * @brief Controlador de ejecución de comandos de actuadores
 * 
 * Gestiona la ejecución física de comandos sobre los actuadores
 * del sistema de riego, controlando estados y temporizaciones.
 */

/**
 * @class EjecucionComandos
 * @brief Controla la ejecución física de comandos en los actuadores
 * 
 * Esta clase se encarga de gestionar el estado de los pines GPIO
 * correspondientes a bombas y válvulas, implementando la lógica
 * de activación/desactivación con control de tiempos.
 */
class EjecucionComandos {
  private:
    // Variables internas que SOLO esta clase usa
    int** pines_bombas;     ///< Array 2D de pines de actuadores
    int filas_bombas;       ///< Número de filas en el array de pines
    int columnas_bombas;    ///< Número de columnas en el array de pines

    /**
     * @brief Configura el estado físico de un pin de actuador
     * @param actuador Tipo de actuador (fila en el array)
     * @param numero Número específico del actuador (columna en el array)
     * @param estado Estado a establecer (HIGH/LOW)
     * 
     * Método interno que realiza la escritura física en el pin GPIO
     * correspondiente al actuador especificado.
     */
    void configurarPin(int actuador, int numero, int estado);

  public:
    /**
     * @brief Constructor de la clase EjecucionComandos
     * @param pines Array 2D con la configuración de pines GPIO
     * @param filas Número de filas del array de pines
     * @param columnas Número de columnas del array de pines
     * 
     * Inicializa el controlador con la configuración de hardware
     * específica del sistema.
     */
    EjecucionComandos(int** pines, int filas, int columnas);

    // Métodos principales que otros pueden usar
    
    /**
     * @brief Inicia la ejecución de un comando específico
     * @param idx Índice del comando en el array
     * @param comandos Array de estructuras Comando
     * 
     * Activa el comando especificado, estableciendo el pin correspondiente
     * y registrando el tiempo de inicio para control de duración.
     */
    void iniciarComando(int idx, Comando comandos[]);
    
    /**
     * @brief Finaliza la ejecución de un comando específico
     * @param idx Índice del comando en el array
     * @param comandos Array de estructuras Comando
     * 
     * Desactiva el comando especificado, estableciendo el pin en LOW
     * y marcando el comando como inactivo.
     */
    void terminarComando(int idx, Comando comandos[]);
    
    /**
     * @brief Carga comandos desde formato array a estructuras Comando
     * @param origen Array bidimensional con comandos en formato numérico
     * @param destino Array de estructuras Comando para almacenar resultado
     * @param num_comandos Número de comandos a cargar
     * 
     * Convierte los datos de comandos desde formato de array simple
     * a estructuras Comando completas con toda la información necesaria.
     */
    void cargarComandos(int origen[10][4], Comando destino[], int num_comandos);

    /**
     * @brief Verifica si un comando está actualmente activo
     * @param idx Índice del comando a verificar
     * @param comandos Array de estructuras Comando
     * @return true si el comando está activo, false en caso contrario
     */
    bool estaActivo(int idx, Comando comandos[]);
};

#endif