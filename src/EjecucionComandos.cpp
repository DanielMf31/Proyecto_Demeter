/**
 * @file EjecucionComandos.cpp
 * @brief Implementación del controlador de ejecución de comandos
 * 
 * Contiene la implementación de los métodos para controlar
 * físicamente los actuadores del sistema de riego.
 */

#include "EjecucionComandos.h"
#include "Configuracion.h"

/**
 * @brief Constructor de la clase EjecucionComandos
 * @param pines Array 2D con la configuración de pines GPIO
 * @param filas Número de filas del array de pines
 * @param columnas Número de columnas del array de pines
 * 
 * Inicializa el controlador con la configuración de hardware
 * y prepara las estructuras internas para la gestión de comandos.
 */
EjecucionComandos::EjecucionComandos(int** pines, int filas, int columnas) {
    pines_bombas = pines;
    filas_bombas = filas;
    columnas_bombas = columnas;
}

// MÉTODO PRIVADO

/**
 * @brief Configura el estado físico de un pin de actuador
 * @param actuador Tipo de actuador (fila en el array)
 * @param numero Número específico del actuador (columna en el array)
 * @param estado Estado a establecer (HIGH/LOW)
 * 
 * Realiza la validación de índices y ejecuta la escritura física
 * en el pin GPIO correspondiente. Solo afecta al hardware si
 * los parámetros están dentro de los rangos válidos.
 */
void EjecucionComandos::configurarPin(int actuador, int numero, int estado) {
    if (actuador >= 0 && actuador < filas_bombas && 
        numero >= 0 && numero < columnas_bombas) {
        digitalWrite(pines_bombas[actuador][numero], estado);
    }
}

// MÉTODOS PÚBLICOS

/**
 * @brief Inicia la ejecución de un comando específico
 * @param idx Índice del comando en el array (0-9)
 * @param comandos Array de estructuras Comando
 * 
 * Activa el comando especificado marcándolo como activo,
 * registrando el tiempo de inicio y estableciendo el estado
 * físico del pin correspondiente.
 * 
 * @note El índice debe estar en el rango 0-9 para ser procesado
 */
void EjecucionComandos::iniciarComando(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        comandos[idx].activo = true;
        comandos[idx].inicio = millis();
        configurarPin(comandos[idx].actuador, comandos[idx].numero, comandos[idx].estado);
    }
}

/**
 * @brief Finaliza la ejecución de un comando específico
 * @param idx Índice del comando en el array (0-9)
 * @param comandos Array de estructuras Comando
 * 
 * Desactiva el comando especificado marcándolo como inactivo
 * y estableciendo el estado físico del pin en LOW (desactivado).
 * 
 * @note El índice debe estar en el rango 0-9 para ser procesado
 */
void EjecucionComandos::terminarComando(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        comandos[idx].activo = false;
        configurarPin(comandos[idx].actuador, comandos[idx].numero, LOW);
    }
}

/**
 * @brief Carga comandos desde formato array a estructuras Comando
 * @param origen Array bidimensional con comandos en formato numérico
 * @param destino Array de estructuras Comando para almacenar resultado
 * @param num_comandos Número de comandos a cargar
 * 
 * Convierte los datos desde el formato de array simple (4 valores por comando)
 * a estructuras Comando completas, inicializando los campos de control
 * de ejecución (activo, inicio) a sus valores por defecto.
 * 
 * @note Solo procesa hasta 10 comandos máximo
 */
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

/**
 * @brief Verifica si un comando está actualmente activo
 * @param idx Índice del comando a verificar (0-9)
 * @param comandos Array de estructuras Comando
 * @return true si el comando está activo, false en caso contrario o índice inválido
 * 
 * Proporciona información sobre el estado de ejecución de un comando
 * específico, útil para verificar el progreso de secuencias de comandos.
 */
bool EjecucionComandos::estaActivo(int idx, Comando comandos[]) {
    if (idx >= 0 && idx < 10) {
        return comandos[idx].activo;
    }
    return false;
}