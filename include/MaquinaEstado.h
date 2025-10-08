#ifndef MAQUINA_ESTADO_H
#define MAQUINA_ESTADO_H

#include <Arduino.h>
#include "Configuracion.h"
#include "EjecucionComandos.h"
#include "ProcesamientoDatos.h"

/**
 * @file MaquinaEstado.h
 * @brief Definición de la máquina de estados principal del sistema
 * 
 * Controla el flujo de operación del sistema de riego mediante
 * una máquina de estados finitos con cuatro estados principales.
 */

/**
 * @class MaquinaEstado
 * @brief Máquina de estados que gestiona el ciclo de operación del sistema
 * 
 * Esta clase implementa una máquina de estados finitos que controla
 * las transiciones entre los diferentes modos de operación del sistema
 * de riego automatizado.
 */
class MaquinaEstado {
  private:
    // VARIABLES PRIVADAS
    int estadoActual;                       ///< Estado actual de la máquina de estados
    unsigned long ultimaVerificacion;       ///< Última marca de tiempo de verificación
    unsigned long intervaloVerificacion;    ///< Intervalo entre verificaciones (ms)
    ProcesamientoDatos& procesador;         ///< Referencia al procesador de datos
    EjecucionComandos& ejecutor;            ///< Referencia al ejecutor de comandos
    
    // MÉTODOS PRIVADOS
    /**
     * @brief Verifica si hay comandos disponibles en el UART
     * @return true si hay datos disponibles, false en caso contrario
     */
    bool hayComandosUART();
    
    /**
     * @brief Verifica si hay comandos pendientes de ejecución
     * @return true si hay comandos pendientes, false en caso contrario
     */
    bool hayComandosPendientes();
    
    /**
     * @brief Cambia el estado actual de la máquina
     * @param nuevoEstado Nuevo estado a establecer
     */
    void cambiarEstado(int nuevoEstado);
    
    /**
     * @brief Ejecuta las acciones correspondientes al estado ESPERA
     */
    void EstadoEspera();
    
    /**
     * @brief Ejecuta las acciones correspondientes al estado EJECUCIÓN
     * @param comandoActual Índice del comando actual en ejecución
     * @param numero_comandos Número total de comandos a ejecutar
     * @param comandos_parsed Array de comandos parseados para ejecución
     */
    void EstadoEjecucion(int comandoActual, int numero_comandos, Comando* comandos_parsed);
    
    /**
     * @brief Ejecuta las acciones correspondientes al estado RECIBIENDO
     * @param destino Array donde almacenar comandos sin procesar
     * @param struct_comandos_local_parsed Array de estructuras Comando parseadas
     */
    void EstadoRecibiendo(int destino[100][4], Comando struct_comandos_local_parsed[100]);
    
    /**
     * @brief Ejecuta las acciones correspondientes al estado ERROR
     */
    void EstadoError();

  public:
    // CONSTANTES PÚBLICAS
    static const int ESTADO_ESPERA = 0;     ///< Estado de espera de comandos
    static const int ESTADO_EJECUCION = 1;  ///< Estado de ejecución de comandos
    static const int ESTADO_RECIBIENDO = 2; ///< Estado de recepción de datos
    static const int ESTADO_ERROR = 3;      ///< Estado de error del sistema

    /**
     * @brief Constructor de la máquina de estados
     * @param proc Referencia al procesador de datos
     * @param ej Referencia al ejecutor de comandos
     */
    MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej);
    
    // MÉTODOS PÚBLICOS
    
    /**
     * @brief Actualiza el estado de la máquina basado en condiciones actuales
     */
    void actualizar();
    
    /**
     * @brief Obtiene el estado actual de la máquina
     * @return Estado actual como entero
     */
    int getEstadoActual();
    
    /**
     * @brief Obtiene el nombre del estado actual
     * @return String con el nombre del estado actual
     */
    String getNombreEstado();
    
    /**
     * @brief Establece el intervalo de verificación entre estados
     * @param intervalo Intervalo en milisegundos
     */
    void setIntervaloVerificacion(unsigned long intervalo);
    
    /**
     * @brief Ejecuta la acción correspondiente al estado actual
     * @param estadoActual Estado actual de la máquina
     */
    void ActuacionMaquinaEstados(int estadoActual);
};

#endif