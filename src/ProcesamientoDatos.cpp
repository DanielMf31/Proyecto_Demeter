#include "ProcesamientoDatos.h"

// Constructor
ProcesamientoDatos::ProcesamientoDatos() {
    comandoCount = 0;
    for(int i = 0; i < 4; i++) {
        valores[i] = 0;
    }
    
    // Inicializar arrays
    for(int i = 0; i < 2; i++) {
        for(int j = 0; j < 4; j++) {
            comandos_unparsed[i][j] = 0;
        }
    }
    
    for(int i = 0; i < 10; i++) {
        comandos_parsed[i] = {0, 0, 0, 0, false, 0};
    }
    
    numero_comandos = 2;  // Por los comandos de prueba
    ComandoActual = 0;
}

// Implementación de procesarMensaje
void ProcesamientoDatos::procesarMensaje(String mensajeRecibido, int destino[100][4]) {
    int start = 0;
    int index = 0;
    
    // Reiniciar valores array
    for(int i = 0; i < 4; i++) {
        valores[i] = 0;
    }
    
    // Recorrer cada carácter del mensaje
    for (int i = 0; i <= mensajeRecibido.length(); i++) {
        // Si encontramos un espacio O llegamos al final
        if (mensajeRecibido[i] == ' ' || i == mensajeRecibido.length()) {
            String numeroStr = mensajeRecibido.substring(start, i);
            valores[index] = numeroStr.toInt();
            start = i + 1;
            index++;
            
            // Si ya tenemos 4 números, salir
            if (index >= 4) break;
        }
    }
    
    // Guardar en el array destino SOLO UNA VEZ
    for(int j = 0; j < 4; j++) {
        destino[comandoCount][j] = valores[j];
    }
    
    comandoCount++;
    
    // Protección para no exceder el tamaño del array
    if (comandoCount >= 100) {
        comandoCount = 0;
    }
}

// Implementación de cargarComandos
void ProcesamientoDatos::cargarComandos(int origen[10][4], Comando destino[]) {
    for(int i = 0; i < 10; i++) {
        destino[i].actuador = origen[i][0];
        destino[i].numero = origen[i][1];
        destino[i].estado = origen[i][2];
        destino[i].duracion = origen[i][3];
        destino[i].activo = false;
        destino[i].inicio = 0;
    }
}

// Implementación de LeerMensajesUART
void ProcesamientoDatos::LeerMensajesUART(int destino[100][4]) {
    while (Serial2.available() > 0) {
        String mensaje = Serial2.readStringUntil('\n');
        mensaje.trim();
        
        Serial.print("Recibido: ");
        Serial.println(mensaje);
        
        // Llamar a procesarMensaje con el array destino
        procesarMensaje(mensaje, destino);
    }
}

// Implementación de getters
Comando* ProcesamientoDatos::getComandosParsed() { 
    return comandos_parsed; 
}

int (*ProcesamientoDatos::getComandosUnparsed())[4] { 
    return comandos_unparsed; 
}

int ProcesamientoDatos::getComandoCount() { 
    return comandoCount; 
}

int ProcesamientoDatos::getComandoActual() { 
    return ComandoActual; 
}

int ProcesamientoDatos::getNumeroComandos() { 
    return numero_comandos;  // Cambiado de comandoCount a numero_comandos
}

// Implementación de setters
void ProcesamientoDatos::incrementarComandoActual() { 
    ComandoActual++; 
}

void ProcesamientoDatos::resetArrayComandos() {
    // Implementación pendiente
}