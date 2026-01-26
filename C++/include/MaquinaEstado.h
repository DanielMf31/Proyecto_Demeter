#ifndef MAQUINAESTADO_H
#define MAQUINAESTADO_H

#include <Arduino.h>
#include "ProtocoloComunicacion.h"
#include "EjecucionComandos.h"

class MaquinaEstado {
private:
    ProtocoloComunicacion& protocolo;
    EjecucionComandos& ejecutor;
    
    // Estados de la máquina
    int estadoMaquina;
    unsigned long ultimaVerificacion;
    unsigned long intervaloVerificacion;
    
    // Comandos locales para ejecución
    int comandosLocales[100][5];
    int comandoCountLocal;
    
    // Control de ejecución
    int indiceComandoActual;
    unsigned long tiempoInicioComando;
    bool comandoEnEjecucion;
    
    
    
    // Métodos privados
    void cambiarEstado(int nuevoEstado);
    void procesarComandosRecibidos();
    void ejecutarSiguienteComando();
    void verificarComandoActual();
    void detenerComandoActual();  // ¡DECLARADA PERO FALTABA IMPLEMENTACIÓN!
    
public:
    MaquinaEstado(ProtocoloComunicacion& prot, EjecucionComandos& ej);
    

    // Estados de la máquina
    static const int ESTADO_INICIAL = 0;
    static const int ESTADO_ESPERA = 1;
    static const int ESTADO_RECIBIENDO = 2;
    static const int ESTADO_EJECUTANDO = 3;
    static const        ESTADO_COMPLETADO = 4,
        ESTADO_ERROR = 5,
        ESTADO_EJECUCION_DIRECTA = 6;
    
    // Métodos principales
    void inicializar();
    void actualizar();
    
    // Control manual
    void iniciarRecepcion();
    void iniciarEjecucion();
    void detenerEjecucion();
    void resetear();
    
    // Getters
    int getEstado() const { return estadoMaquina; }
    String getEstadoTexto() const;
    int getComandosPendientes() const;
    int getComandoActual() const { return indiceComandoActual; }
    
    // Estado del sistema
    struct EstadoSistema {
        int estadoMaquina;
        int estadoProtocolo;
        int comandosCargados;
        int comandoActual;
        bool comandoActivo;
        String estadoTextoMaquina;
        String estadoTextoProtocolo;
    };
    
    EstadoSistema getEstadoCompleto();
    
    // Para comandos directos
    void ejecutarComandoDirecto(int actuador, int duracionMs);
};

#endif