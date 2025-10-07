#include "ProcesamientoDatos.h"

/**
 * @brief Constructor de la clase ProcesamientoDatos
 * 
 * Inicializa todos los arrays y variables de estado
 * a sus valores por defecto.
 */
ProcesamientoDatos::ProcesamientoDatos() {
    comandoCount = 0;
    
    // Inicializar array valores
    for(int i = 0; i < 4; i++) {
        valores[i] = 0;
    }
    
    // Inicializar array comandos_unparsed
    for(int i = 0; i < 100; i++) {
        for(int j = 0; j < 4; j++) {
            comandos_unparsed[i][j] = 0;
        }
    }
    
    // ✅ INICIALIZAR array comandos_parsed (que faltaba)
    for(int i = 0; i < 100; i++) {
        comandos_parsed[i] = {0, 0, 0, 0, false, 0};
    }
    
    numero_comandos = 0;
    ComandoActual = 0;
}

/**
 * @brief Lee mensajes UART y los procesa
 * @param destino Array donde se almacenarán los comandos procesados
 * 
 * Monitorea el puerto Serial2 continuamente y procesa los mensajes
 * recibidos para convertirlos en comandos ejecutables.
 */
void ProcesamientoDatos::LeerMensajesUART(int destino[100][4]) {
    while (Serial2.available() > 0) {
        String mensaje = Serial2.readStringUntil('\n');
        mensaje.trim();
        
        Serial.print("Recibido: ");
        Serial.println(mensaje);
        
        procesarMensaje(mensaje, destino);
    }
}

/**
 * @brief Procesa un mensaje de texto y lo convierte en comandos numéricos
 * @param mensajeRecibido String con el mensaje a procesar
 * @param destino Array donde se almacenarán los valores extraídos
 * 
 * Convierte un mensaje de texto con números separados por espacios
 * en un array de enteros para su posterior ejecución.
 */
void ProcesamientoDatos::procesarMensaje(String mensajeRecibido, int destino[100][4]) {
    int start = 0;
    int index = 0;
    
    // Reiniciar valores array
    for(int i = 0; i < 4; i++) {
        valores[i] = 0;
    }
    
    // Recorrer cada carácter del mensaje
    for (int i = 0; i <= mensajeRecibido.length(); i++) {
        if (mensajeRecibido[i] == ' ' || i == mensajeRecibido.length()) {
            String numeroStr = mensajeRecibido.substring(start, i);
            valores[index] = numeroStr.toInt();
            start = i + 1;
            index++;
            
            if (index >= 4) break;
        }
    }
    
    // Guardar en el array destino
    for(int j = 0; j < 4; j++) {
        destino[comandoCount][j] = valores[j];
    }
    
    comandoCount++;
    
    if (comandoCount >= 100) {
        comandoCount = 0;
    }
}

/**
 * @brief Carga comandos desde array unparsed a array parsed
 * @param origen Array con comandos en formato numérico
 * @param destino Array de estructuras Comando
 * 
 * Convierte los arrays bidimensionales de enteros en estructuras
 * Comando con toda la información necesaria para su ejecución.
 */
void ProcesamientoDatos::cargarComandos(int origen[100][4], Comando destino[100]) {
    for(int i = 0; i < 100; i++) {
        destino[i].actuador = origen[i][0];
        destino[i].numero = origen[i][1];
        destino[i].estado = origen[i][2];
        destino[i].duracion = origen[i][3];
        destino[i].activo = false;
        destino[i].inicio = 0;
    }
}

// GETTERS con documentación

/**
 * @brief Obtiene una copia de los comandos sin procesar
 * @param destino Array donde se copiarán los comandos unparsed
 */
void ProcesamientoDatos::getComandosUnparsed(int destino[100][4]) { 
    for(int i = 0; i < 100; i++) {
        for(int j = 0; j < 4; j++) {
            destino[i][j] = comandos_unparsed[i][j];
        }
    }
}

/**
 * @brief Obtiene el contador actual de comandos
 * @return Número de comandos procesados
 */
int ProcesamientoDatos::getComandoCount() { 
    return comandoCount; 
}

/**
 * @brief Obtiene el índice del comando actual en ejecución
 * @return Índice del comando actual
 */
int ProcesamientoDatos::getComandoActual() { 
    return ComandoActual; 
}

/**
 * @brief Obtiene el número total de comandos
 * @return Número total de comandos en el sistema
 */
int ProcesamientoDatos::getNumeroComandos() { 
    return numero_comandos;
}

/**
 * @brief Incrementa el índice del comando actual
 */
void ProcesamientoDatos::incrementarComandoActual() { 
    ComandoActual++; 
}

/**
 * @brief Reinicia el array de comandos
 * 
 * Restablece todos los comandos a sus valores iniciales
 * y prepara el sistema para una nueva secuencia.
 */
void ProcesamientoDatos::resetArrayComandos() {
    // Implementación pendiente
    comandoCount = 0;
    ComandoActual = 0;
}