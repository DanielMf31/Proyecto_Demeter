// ========================================
// ARCHIVO: ProtocoloComunicacion.cpp
// RUTA: src\Compartidos\ProtocoloComunicacion.cpp
// ========================================

#include "ProtocoloComunicacion.h"

ProtocoloComunicacion::ProtocoloComunicacion(ComunicacionUART& uartCom, bool esTransmisor)
    : uart(uartCom), esTransmisor(esTransmisor), estadoActual(ESTADO_INICIAL),
      comandoCount(0), datosRecibidosCount(0), tiempoEspera(5000),
      tiempoInicioRecepcion(0), recepcionCompleta(false), codigo103Recibido(false) {
    
    // Inicializar arrays
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 5; j++) {
            comandosRecibidos[i][j] = 0;
            datosParaVerificar[i][j] = 0;
        }
    }
    
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            datosParaTransmitir[i][j] = 0;
        }
    }
}

void ProtocoloComunicacion::configurarDatosTransmision(const int datos[5][5]) {
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            datosParaTransmitir[i][j] = datos[i][j];
        }
    }
}

void ProtocoloComunicacion::configurarDatosSimples(int a1_ms, int a2_ms, int a3_ms, int a4_ms, int a5_ms) {
    int datos[5][5] = {
        {1, 1, 0, a1_ms, 0},
        {1, 2, 0, a2_ms, 0},
        {1, 3, 0, a3_ms, 0},
        {1, 4, 0, a4_ms, 0},
        {1, 5, 0, a5_ms, 0}
    };
    configurarDatosTransmision(datos);
}

void ProtocoloComunicacion::procesarMensajeSimple(const String& mensaje, int destino[5]) {
    int valores[5] = {0};
    int index = 0;
    int start = 0;
    
    for (int i = 0; i <= mensaje.length(); i++) {
        if (mensaje[i] == ' ' || i == mensaje.length()) {
            if (start < i && index < 5) {
                String numeroStr = mensaje.substring(start, i);
                valores[index] = numeroStr.toInt();
                index++;
            }
            start = i + 1;
        }
    }
    
    for (int i = 0; i < 5; i++) {
        destino[i] = valores[i];
    }
}

void ProtocoloComunicacion::procesarMensajeCompleto(const String& mensaje, int destino[100][5], int& contador) {
    int valores[5];
    procesarMensajeSimple(mensaje, valores);
    
    if (contador < 100) {
        for (int i = 0; i < 5; i++) {
            destino[contador][i] = valores[i];
        }
        contador++;
    }
}

bool ProtocoloComunicacion::iniciarHandshake() {
    if (!esTransmisor) return false;
    
    enviarCodigo(CODIGO_SOLICITUD_CONEXION);
    estadoActual = ESPERANDO_CONFIRMACION_102;
    tiempoEspera = millis();
    
    Serial.println("[PROTOCOLO] Enviado código 101 - Esperando confirmación...");
    return true;
}

bool ProtocoloComunicacion::transmitirDatos() {
    if (!esTransmisor) return false;
    
    Serial.println("[PROTOCOLO] Transmitiendo 5 comandos...");
    
    for (int i = 0; i < 5; i++) {
        uart.enviarComandoArray(datosParaTransmitir[i]);
        delay(10);
        
        Serial.print("  Enviado: [");
        for (int j = 0; j < 5; j++) {
            Serial.print(datosParaTransmitir[i][j]);
            if (j < 4) Serial.print(", ");
        }
        Serial.println("]");
    }
    
    Serial.println("[PROTOCOLO] Esperando código 103...");
    return true;
}

void ProtocoloComunicacion::esperarYEnviar103YDatos() {
    if (esTransmisor) return;
    
    if (comandoCount >= 5 && !recepcionCompleta) {
        Serial.println("[PROTOCOLO] Enviando código 103 y datos de vuelta...");
        
        enviarCodigo(CODIGO_DATOS_RECIBIDOS);
        delay(50);
        
        for (int i = 0; i < comandoCount; i++) {
            uart.enviarComandoArray(comandosRecibidos[i]);
            delay(10);
        }
        
        recepcionCompleta = true;
        estadoActual = VERIFICANDO_DATOS;
    }
}

bool ProtocoloComunicacion::datosSonIguales() {
    if (datosRecibidosCount != 5) return false;
    
    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            if (datosParaVerificar[i][j] != datosParaTransmitir[i][j]) {
                Serial.print("[PROTOCOLO] Diferencia encontrada en [");
                Serial.print(i);
                Serial.print("][");
                Serial.print(j);
                Serial.print("]: ");
                Serial.print(datosParaVerificar[i][j]);
                Serial.print(" != ");
                Serial.println(datosParaTransmitir[i][j]);
                return false;
            }
        }
    }
    return true;
}

void ProtocoloComunicacion::verificarDatosRecibidos() {
    if (!esTransmisor || datosRecibidosCount < 5) return;
    
    bool sonIguales = datosSonIguales();
    
    if (sonIguales) {
        Serial.println("[PROTOCOLO] Verificación CORRECTA - Enviando código 104");
        enviarCodigo(CODIGO_VERIFICACION_CORRECTA);
        estadoActual = COMUNICACION_COMPLETADA;
    } else {
        Serial.println("[PROTOCOLO] Verificación FALLIDA - Enviando código 105");
        enviarCodigo(CODIGO_ERROR_VERIFICACION);
        estadoActual = ERROR_COMUNICACION;
    }
    
    codigo103Recibido = false;
}

void ProtocoloComunicacion::iniciarProtocolo() {
    if (!esTransmisor) return;
    
    if (estadoActual != ESTADO_INICIAL && estadoActual != COMUNICACION_COMPLETADA && 
        estadoActual != ERROR_COMUNICACION && estadoActual != ERROR_TIMEOUT) {
        Serial.println("[PROTOCOLO] Protocolo ya en curso");
        return;
    }
    
    reset();
    iniciarHandshake();
    Serial.println("[PROTOCOLO] Protocolo iniciado");
}

void ProtocoloComunicacion::procesarComunicacionTransmisor() {
    if (!esTransmisor) return;
    
    while (uart.hayDatosDisponibles()) {
        String mensaje = uart.recibir();
        if (mensaje.length() == 0) continue;
        
        int espacioPos = mensaje.indexOf(' ');
        String codigoStr = (espacioPos != -1) ? mensaje.substring(0, espacioPos) : mensaje;
        int codigo = codigoStr.toInt();
        
        // Procesar códigos del protocolo
        switch (codigo) {
            case CODIGO_CONFIRMACION_CONEXION:
                if (estadoActual == ESPERANDO_CONFIRMACION_102) {
                    Serial.println("[PROTOCOLO] Recibido código 102 - Iniciando transmisión");
                    estadoActual = TRANSMITIENDO_DATOS;
                    transmitirDatos();
                }
                break;
                
            case CODIGO_DATOS_RECIBIDOS:
                if (estadoActual == TRANSMITIENDO_DATOS) {
                    Serial.println("[PROTOCOLO] Recibido código 103 - Esperando datos de vuelta");
                    estadoActual = ESPERANDO_103_Y_DATOS;
                    codigo103Recibido = true;
                    tiempoEspera = millis();
                }
                break;
                
            default:
                if (codigo103Recibido && codigo != CODIGO_SOLICITUD_CONEXION && 
                    codigo != CODIGO_VERIFICACION_CORRECTA && codigo != CODIGO_ERROR_VERIFICACION) {
                    procesarMensajeCompleto(mensaje, datosParaVerificar, datosRecibidosCount);
                    
                    if (datosRecibidosCount >= 5) {
                        Serial.println("[PROTOCOLO] 5 comandos recibidos para verificación");
                        verificarDatosRecibidos();
                    }
                }
                break;
        }
    }
    
    // Timeout
    if (estadoActual != COMUNICACION_COMPLETADA && estadoActual != ERROR_COMUNICACION) {
        if (millis() - tiempoEspera > 10000) {
            Serial.println("[PROTOCOLO] Timeout - Sin respuesta");
            estadoActual = ERROR_TIMEOUT;
        }
    }
}

void ProtocoloComunicacion::procesarComunicacionReceptor() {
    if (esTransmisor) return;
    
    while (uart.hayDatosDisponibles()) {
        String mensaje = uart.recibir();
        if (mensaje.length() == 0) continue;
        
        int espacioPos = mensaje.indexOf(' ');
        String codigoStr = (espacioPos != -1) ? mensaje.substring(0, espacioPos) : mensaje;
        int codigo = codigoStr.toInt();
        
        // Procesar códigos del protocolo
        switch (codigo) {
            case CODIGO_SOLICITUD_CONEXION:
                Serial.println("[PROTOCOLO] Recibido código 101 - Confirmando conexión");
                estadoActual = ESPERANDO_CONFIRMACION_102;
                enviarCodigo(CODIGO_CONFIRMACION_CONEXION);
                break;
                
            case CODIGO_VERIFICACION_CORRECTA:
                if (estadoActual == VERIFICANDO_DATOS) {
                    Serial.println("[PROTOCOLO] Recibido código 104 - Comunicación exitosa");
                    estadoActual = COMUNICACION_COMPLETADA;
                }
                break;
                
            case CODIGO_ERROR_VERIFICACION:
                if (estadoActual == VERIFICANDO_DATOS) {
                    Serial.println("[PROTOCOLO] Recibido código 105 - Error en verificación");
                    estadoActual = ERROR_COMUNICACION;
                }
                break;
                
            default:
                if (estadoActual == ESPERANDO_CONFIRMACION_102 && 
                    codigo != CODIGO_CONFIRMACION_CONEXION && 
                    codigo != CODIGO_DATOS_RECIBIDOS) {
                    procesarMensajeCompleto(mensaje, comandosRecibidos, comandoCount);
                    
                    if (comandoCount == 5) {
                        Serial.println("[PROTOCOLO] 5 comandos recibidos - Confirmando recepción");
                        esperarYEnviar103YDatos();
                    }
                }
                break;
        }
    }
}

void ProtocoloComunicacion::getComandos(int destino[100][5]) {
    for (int i = 0; i < comandoCount; i++) {
        for (int j = 0; j < 5; j++) {
            destino[i][j] = comandosRecibidos[i][j];
        }
    }
}

String ProtocoloComunicacion::getEstadoTexto() const {
    switch (estadoActual) {
        case ESTADO_INICIAL: return "INICIAL";
        case ESPERANDO_CONFIRMACION_102: return "ESPERANDO_102";
        case TRANSMITIENDO_DATOS: return "TRANSMITIENDO";
        case ESPERANDO_103_Y_DATOS: return "ESPERANDO_103";
        case VERIFICANDO_DATOS: return "VERIFICANDO";
        case COMUNICACION_COMPLETADA: return "COMPLETADA";
        case ERROR_COMUNICACION: return "ERROR_COM";
        case ERROR_TIMEOUT: return "ERROR_TIMEOUT";
        default: return "DESCONOCIDO";
    }
}

void ProtocoloComunicacion::reset() {
    comandoCount = 0;
    datosRecibidosCount = 0;
    estadoActual = ESTADO_INICIAL;
    recepcionCompleta = false;
    codigo103Recibido = false;
    tiempoEspera = millis();
    tiempoInicioRecepcion = 0;
    
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 5; j++) {
            comandosRecibidos[i][j] = 0;
            datosParaVerificar[i][j] = 0;
        }
    }
    
    uart.limpiarBuffer();
    Serial.println("[PROTOCOLO] Reset completado");
}

void ProtocoloComunicacion::enviarCodigo(int codigo) {
    uart.enviarComando(codigo, 0, 0, 0, 0);
}

// Métodos de utilidad (mantenidos por compatibilidad)
void ProtocoloComunicacion::mostrarComandosRecibidos() {
    if (comandoCount == 0) {
        Serial.println("No hay comandos recibidos");
        return;
    }
    
    Serial.println("\n=== COMANDOS RECIBIDOS ===");
    for (int i = 0; i < comandoCount; i++) {
        Serial.print("[");
        for (int j = 0; j < 5; j++) {
            Serial.print(comandosRecibidos[i][j]);
            if (j < 4) Serial.print(", ");
        }
        Serial.println("]");
    }
    Serial.println("==========================\n");
}

void ProtocoloComunicacion::mostrarDatosParaTransmitir() {
    if (!esTransmisor) return;
    
    Serial.println("\n=== DATOS PARA TRANSMITIR ===");
    for (int i = 0; i < 5; i++) {
        Serial.print("[");
        for (int j = 0; j < 5; j++) {
            Serial.print(datosParaTransmitir[i][j]);
            if (j < 4) Serial.print(", ");
        }
        Serial.println("]");
    }
    Serial.println("============================\n");
}

void ProtocoloComunicacion::mostrarDatosParaVerificar() {
    if (!esTransmisor || datosRecibidosCount == 0) return;
    
    Serial.println("\n=== DATOS PARA VERIFICAR ===");
    for (int i = 0; i < datosRecibidosCount; i++) {
        Serial.print("[");
        for (int j = 0; j < 5; j++) {
            Serial.print(datosParaVerificar[i][j]);
            if (j < 4) Serial.print(", ");
        }
        Serial.println("]");
    }
    Serial.println("============================\n");
}