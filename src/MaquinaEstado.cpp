/**
 * @file MaquinaEstado.cpp
 * @brief Implementación de la máquina de estados principal
 * 
 * Contiene la implementación de todos los métodos de la clase
 * MaquinaEstado que controla el flujo de operación del sistema.
 */

#include "MaquinaEstado.h"
#include "ProcesamientoDatos.h"

/**
 * @brief Constructor de la clase MaquinaEstado
 * @param proc Referencia al procesador de datos
 * @param ej Referencia al ejecutor de comandos
 * 
 * Inicializa la máquina de estados con valores por defecto
 * y establece las referencias a las dependencias.
 */
MaquinaEstado::MaquinaEstado(ProcesamientoDatos& proc, EjecucionComandos& ej) 
    : procesador(proc), ejecutor(ej) {
    estadoActual = ESTADO_ESPERA;
    ultimaVerificacion = 0;
    intervaloVerificacion = 100;
}

// MÉTODOS PRIVADOS

/**
 * @brief Verifica si hay comandos disponibles en el UART
 * @return true si hay datos disponibles, false en caso contrario
 */
bool MaquinaEstado::hayComandosUART() {
    return (Serial2.available() > 0);
}

/**
 * @brief Verifica si hay comandos pendientes de ejecución
 * @return true si hay comandos pendientes, false en caso contrario
 * @todo Implementar la lógica de verificación de comandos pendientes
 */
bool MaquinaEstado::hayComandosPendientes() {
    // TODO: Implementar lógica de verificación
    return false;
}

/**
 * @brief Cambia el estado actual de la máquina
 * @param nuevoEstado Nuevo estado a establecer
 * 
 * Realiza la transición entre estados y registra el cambio
 * en el puerto serial para depuración.
 */
void MaquinaEstado::cambiarEstado(int nuevoEstado) {
    if (nuevoEstado != estadoActual) {
        Serial.print("Cambiando estado: ");
        Serial.print(estadoActual);
        Serial.print(" -> ");
        Serial.println(nuevoEstado);
        estadoActual = nuevoEstado;
    }
}

// MÉTODOS PÚBLICOS

/**
 * @brief Ejecuta las acciones correspondientes al estado ESPERA
 * @todo Implementar las acciones específicas del estado de espera
 */
void MaquinaEstado::EstadoEspera() {
    // TODO: Implementar acciones del estado espera
}

/**
 * @brief Ejecuta las acciones correspondientes al estado EJECUCIÓN
 * @param comandoActual Índice del comando actual en ejecución
 * @param numero_comandos Número total de comandos a ejecutar
 * @param comandos_parsed Array de comandos parseados para ejecución
 * 
 * Gestiona la ejecución secuencial de comandos, verificando tiempos
 * y realizando las transiciones entre comandos.
 */
void MaquinaEstado::EstadoEjecucion(int comandoActual, int numero_comandos, Comando* comandos_parsed) {
    if(comandoActual < numero_comandos && comandos_parsed[comandoActual].activo) {
        unsigned long ahora = millis();

        // Verificar si el comando actual ha completado su duración
        if(ahora - comandos_parsed[comandoActual].inicio >= comandos_parsed[comandoActual].duracion) {
            ejecutor.terminarComando(comandoActual, comandos_parsed);
            procesador.incrementarComandoActual();
            comandoActual = procesador.getComandoActual();
        }

        // Ejecutar siguiente comando si existe
        if(comandoActual < numero_comandos) {
            ejecutor.iniciarComando(comandoActual, comandos_parsed);
        } else {
            // Todos los comandos completados, volver a espera
            cambiarEstado(ESTADO_ESPERA);
            procesador.resetArrayComandos();
        }
    }
}

/**
 * @brief Ejecuta las acciones correspondientes al estado ERROR
 * @todo Implementar el manejo de errores del sistema
 */
void MaquinaEstado::EstadoError() {
    // TODO: Implementar manejo de errores
}

/**
 * @brief Ejecuta las acciones correspondientes al estado RECIBIENDO
 * @param destino Array donde almacenar comandos sin procesar
 * @param struct_comandos_local_parsed Array de estructuras Comando parseadas
 * 
 * Lee datos del UART, los procesa y carga en las estructuras de comandos
 * para su posterior ejecución.
 */
void MaquinaEstado::EstadoRecibiendo(int destino[100][4], Comando struct_comandos_local_parsed[100]) {
    procesador.LeerMensajesUART(destino);
    procesador.cargarComandos(destino, struct_comandos_local_parsed);
}

/**
 * @brief Actualiza el estado de la máquina basado en condiciones actuales
 * 
 * Verifica periódicamente las condiciones del sistema y realiza
 * las transiciones de estado correspondientes.
 */
void MaquinaEstado::actualizar() {
    unsigned long ahora = millis();
    
    // Verificar si ha pasado el intervalo de verificación
    if (ahora - ultimaVerificacion < intervaloVerificacion) {
        return;
    }
    ultimaVerificacion = ahora;
    
    // Lógica de transición de estados
    if (hayComandosUART()) {
        cambiarEstado(ESTADO_RECIBIENDO);
    } 
    else if (hayComandosPendientes()) {
        cambiarEstado(ESTADO_EJECUCION);
    }
    else {
        cambiarEstado(ESTADO_ESPERA);
    }
}

/**
 * @brief Obtiene el estado actual de la máquina
 * @return Estado actual como entero
 */
int MaquinaEstado::getEstadoActual() {
    return estadoActual;
}

/**
 * @brief Obtiene el nombre del estado actual
 * @return String con el nombre del estado actual
 */
String MaquinaEstado::getNombreEstado() {
    switch(estadoActual) {
        case ESTADO_ESPERA: return "ESPERA";
        case ESTADO_EJECUCION: return "EJECUCION"; 
        case ESTADO_RECIBIENDO: return "RECIBIENDO";
        case ESTADO_ERROR: return "ERROR";
        default: return "DESCONOCIDO";
    }
}

// SETTERS

/**
 * @brief Establece el intervalo de verificación entre estados
 * @param intervalo Intervalo en milisegundos
 */
void MaquinaEstado::setIntervaloVerificacion(unsigned long intervalo) {
    intervaloVerificacion = intervalo;
}

/**
 * @brief Ejecuta la acción correspondiente al estado actual
 * @param estadoActual Estado actual de la máquina
 * 
 * Este método centraliza la ejecución de las acciones específicas
 * de cada estado de la máquina de estados.
 */
void MaquinaEstado::ActuacionMaquinaEstados(int estadoActual) {
    int comandoActual = procesador.getComandoActual();
    int numero_comandos = procesador.getNumeroComandos();
    int array_comandos_local_unparsed[100][4];
    Comando struct_comandos_local_parsed[100];

    // Obtener copia local de los comandos
    procesador.getComandosUnparsed(array_comandos_local_unparsed);
    
    // Ejecutar acción según estado actual
    switch(estadoActual) {
        case ESTADO_ESPERA:
            EstadoEspera();
            break;

        case ESTADO_EJECUCION:
            EstadoEjecucion(comandoActual, numero_comandos, struct_comandos_local_parsed);
            break;

        case ESTADO_RECIBIENDO:
            EstadoRecibiendo(array_comandos_local_unparsed, struct_comandos_local_parsed);
            break;

        default:
            // Estado no reconocido, podría manejarse como error
            break;
    }
}