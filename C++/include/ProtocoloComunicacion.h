// ========================================
// ARCHIVO: ProtocoloComunicacion.h
// RUTA: include\ProtocoloComunicacion.h
// ========================================

#ifndef PROTOCOLOCOMUNICACION_H
#define PROTOCOLOCOMUNICACION_H

#include <Arduino.h>
#include "ComunicacionUART.h"

class ProtocoloComunicacion {
public:
    // Estados del protocolo
    static const int ESTADO_INICIAL = 0;
    static const int ESPERANDO_CONFIRMACION_102 = 1;
    static const int TRANSMITIENDO_DATOS = 2;
    static const int ESPERANDO_103_Y_DATOS = 3;
    static const int VERIFICANDO_DATOS = 4;
    static const int COMUNICACION_COMPLETADA = 5;
    static const int ERROR_COMUNICACION = 6;
    static const int ERROR_TIMEOUT = 7;
    static const int EJECUCION_DIRECTA = 8; // Added EJECUCION_DIRECTA with a new value
    
    // Códigos del protocolo
    static const int CODIGO_SOLICITUD_CONEXION = 101;
    static const int CODIGO_CONFIRMACION_CONEXION = 102;
    static const int CODIGO_DATOS_RECIBIDOS = 103;
    static const int CODIGO_VERIFICACION_CORRECTA = 104;
    static const int CODIGO_ERROR_VERIFICACION = 105;
    static const int CODIGO_EJECUCION_DIRECTA = 200;
    
private:
    ComunicacionUART& uart;
    bool esTransmisor;
    
    // Datos del protocolo
    int comandosRecibidos[100][5];
    int datosParaTransmitir[5][5];
    int datosParaVerificar[100][5];
    
    // Control del protocolo
    int estadoActual;
    int comandoCount;
    int datosRecibidosCount;
    
    unsigned long tiempoEspera;
    unsigned long tiempoInicioRecepcion;
    
    bool recepcionCompleta;
    bool codigo103Recibido;
    
    // Métodos privados
    void procesarMensajeSimple(const String& mensaje, int destino[5]);
    void procesarMensajeCompleto(const String& mensaje, int destino[100][5], int& contador);
    
    bool iniciarHandshake();
    bool transmitirDatos();
    void esperarYEnviar103YDatos();
    bool datosSonIguales();
    void verificarDatosRecibidos();
    
public:
    ProtocoloComunicacion(ComunicacionUART& uartCom, bool esTransmisor = false);
    
    // Configuración
    void configurarDatosTransmision(const int datos[5][5]);
    void configurarDatosSimples(int a1_ms, int a2_ms, int a3_ms, int a4_ms, int a5_ms);
    void reset();
    void setTimeOut(unsigned long timeoutMs) { tiempoEspera = timeoutMs; }
    
    // Control del protocolo
    void iniciarProtocolo();
    void procesarComunicacionTransmisor();
    void procesarComunicacionReceptor();
    
    // Getters
    int getEstado() const { return estadoActual; }
    String getEstadoTexto() const;
    
    int getComandoCount() const { return comandoCount; }
    int getDatosRecibidosCount() const { return datosRecibidosCount; }
    
    void getComandos(int destino[100][5]);
    bool esTransmisorMode() const { return esTransmisor; }
    
    // Utilidades
    void mostrarComandosRecibidos();
    void mostrarDatosParaTransmitir();
    void mostrarDatosParaVerificar();
    
    // Para uso directo
    void enviarCodigo(int codigo);
};

#endif