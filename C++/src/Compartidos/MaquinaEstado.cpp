#include "MaquinaEstado.h"

MaquinaEstado::MaquinaEstado(ProtocoloComunicacion& prot, EjecucionComandos& ej) 
    : protocolo(prot), ejecutor(ej), estadoMaquina(ESTADO_INICIAL),
      ultimaVerificacion(0), intervaloVerificacion(100),
      comandoCountLocal(0), indiceComandoActual(0),
      tiempoInicioComando(0), comandoEnEjecucion(false) {
    
    // Inicializar array local
    for (int i = 0; i < 100; i++) {
        for (int j = 0; j < 5; j++) {
            comandosLocales[i][j] = 0;
        }
    }
}

void MaquinaEstado::inicializar() {
    estadoMaquina = ESTADO_ESPERA;
    comandoCountLocal = 0;
    indiceComandoActual = 0;
    comandoEnEjecucion = false;
    
    Serial.println("[MAQUINA] Inicializada - Modo ESPERA");
}

void MaquinaEstado::cambiarEstado(int nuevoEstado) {
    if (nuevoEstado != estadoMaquina) {
        Serial.print("[MAQUINA] Cambio de estado: ");
        Serial.print(getEstadoTexto());
        Serial.print(" -> ");
        
        estadoMaquina = nuevoEstado;
        
        Serial.println(getEstadoTexto());
        
        // Acciones específicas al cambiar estado
        switch (estadoMaquina) {
            case ESTADO_EJECUTANDO:
                indiceComandoActual = 0;
                comandoEnEjecucion = false;
                tiempoInicioComando = 0;
                Serial.println("[MAQUINA] Preparado para ejecucion secuencial");
                break;
                
            case ESTADO_COMPLETADO:
                Serial.println("[MAQUINA] ✓ Ejecucion completada exitosamente");
                comandoEnEjecucion = false;
                break;
                
            case ESTADO_ERROR:
                ejecutor.detenerTodosLosComandos();
                Serial.println("[MAQUINA] Error en el sistema");
                break;
        }
    }
}

void MaquinaEstado::procesarComandosRecibidos() {
    // Verificar estado del protocolo
    int estadoProtocolo = protocolo.getEstado();
    
    if (estadoProtocolo == ProtocoloComunicacion::COMUNICACION_COMPLETADA) {
        Serial.println("[MAQUINA] Protocolo completado, obteniendo comandos...");
        
        // Obtener comandos del protocolo
        protocolo.getComandos(comandosLocales);
        comandoCountLocal = protocolo.getComandoCount();
        
        if (comandoCountLocal > 0) {
            Serial.print("[MAQUINA] ");
            Serial.print(comandoCountLocal);
            Serial.println(" comandos recibidos correctamente");
            
            // Cargar comandos al ejecutor (ACUMULANDO)
            ejecutor.cargarComandosDesdeArray(comandosLocales, comandoCountLocal);
            
            // Cambiar a estado de espera (NO a ejecución automática)
            cambiarEstado(ESTADO_ESPERA);
            Serial.println("[MAQUINA] Comandos guardados. Usa 'e' para ejecutar");
        } else {
            Serial.println("[MAQUINA] Error: No se recibieron comandos");
            cambiarEstado(ESTADO_ERROR);
        }
    }
    else if (estadoProtocolo == ProtocoloComunicacion::ERROR_COMUNICACION || 
             estadoProtocolo == ProtocoloComunicacion::ERROR_TIMEOUT) {
        Serial.println("[MAQUINA] Error en protocolo de comunicación");
        cambiarEstado(ESTADO_ERROR);
    }
}

void MaquinaEstado::ejecutarSiguienteComando() {
    // Verificar si hay comandos para ejecutar
    if (indiceComandoActual >= ejecutor.getComandoCount()) {
        // Todos los comandos ejecutados
        Serial.println("[MAQUINA] ✓ Todos los comandos ejecutados");
        cambiarEstado(ESTADO_COMPLETADO);
        return;
    }
    
    if (!comandoEnEjecucion) {
        // Ejecutar nuevo comando
        Serial.print("[MAQUINA] ▶ Ejecutando comando ");
        Serial.print(indiceComandoActual + 1);
        Serial.print(" de ");
        Serial.print(ejecutor.getComandoCount());
        Serial.print(" - [");
        
        for (int j = 0; j < 5; j++) {
            Serial.print(comandosLocales[indiceComandoActual][j]);
            if (j < 4) Serial.print(", ");
        }
        Serial.println("]");
        
        ejecutor.ejecutarComando(indiceComandoActual);
        comandoEnEjecucion = true;
        tiempoInicioComando = millis();
        
        // Mostrar qué actuador se activa
        int actuador = comandosLocales[indiceComandoActual][1];
        int duracion = comandosLocales[indiceComandoActual][3];
        Serial.print("[MAQUINA] Actuador ");
        Serial.print(actuador);
        Serial.print(" activado por ");
        Serial.print(duracion);
        Serial.println(" ms");
    }
}

void MaquinaEstado::verificarComandoActual() {
    if (!comandoEnEjecucion) return;
    
    // Verificar si el comando actual ha completado su duración
    if (ejecutor.haCompletadoDuracion(indiceComandoActual)) {
        Serial.print("[MAQUINA] ✓ Comando ");
        Serial.print(indiceComandoActual);
        Serial.println(" completado");
        
        ejecutor.detenerComando(indiceComandoActual);
        comandoEnEjecucion = false;
        indiceComandoActual++;
        
        // Pequeña pausa entre comandos (opcional)
        delay(100);
        
        // Mostrar progreso
        if (indiceComandoActual < ejecutor.getComandoCount()) {
            Serial.print("[MAQUINA] Progreso: ");
            Serial.print(indiceComandoActual);
            Serial.print("/");
            Serial.println(ejecutor.getComandoCount());
        }
    }
}

void MaquinaEstado::detenerComandoActual() {
    if (comandoEnEjecucion) {
        Serial.print("[MAQUINA] Deteniendo comando actual (");
        Serial.print(indiceComandoActual);
        Serial.println(")");
        ejecutor.detenerComando(indiceComandoActual);
        comandoEnEjecucion = false;
    }
}

void MaquinaEstado::actualizar() {
    unsigned long ahora = millis();
    
    // Actualización periódica
    if (ahora - ultimaVerificacion < intervaloVerificacion) {
        return;
    }
    ultimaVerificacion = ahora;
    
    // Si somos receptor, procesar comunicación
    if (!protocolo.esTransmisorMode()) {
        protocolo.procesarComunicacionReceptor();
        
        // Verificar si terminamos de recibir
        if (estadoMaquina == ESTADO_RECIBIENDO) {
            procesarComandosRecibidos();
        }
    }
    
    // Ejecutar lógica según estado actual
    switch (estadoMaquina) {
        case ESTADO_ESPERA:
            // Solo esperar
            break;
            
        case ESTADO_RECIBIENDO:
            // La recepción se maneja arriba
            break;
            
        case ESTADO_EJECUTANDO:
            // Verificar si el comando actual terminó
            verificarComandoActual();
            
            // Si no hay comando en ejecución, pasar al siguiente
            if (!comandoEnEjecucion) {
                ejecutarSiguienteComando();
            }
            
            // Verificar completados (por si acaso)
            ejecutor.verificarCompletados();
            break;
            
        case ESTADO_COMPLETADO:
            // Nada que hacer aquí
            break;
            
        case ESTADO_ERROR:
            // Podríamos intentar recuperación automática
            break;
    }
}

void MaquinaEstado::iniciarRecepcion() {
    if (estadoMaquina != ESTADO_ESPERA && estadoMaquina != ESTADO_COMPLETADO) {
        Serial.println("[MAQUINA] Error: No se puede iniciar recepción en estado actual");
        Serial.print("[MAQUINA] Estado actual: ");
        Serial.println(getEstadoTexto());
        return;
    }
    
    if (protocolo.esTransmisorMode()) {
        Serial.println("[MAQUINA] Error: Este dispositivo es transmisor");
        return;
    }
    
    Serial.println("[MAQUINA] Iniciando modo recepción...");
    Serial.println("[MAQUINA] Esperando comunicación del transmisor...");
    
    // Resetear protocolo si está en estado de error
    if (protocolo.getEstado() == ProtocoloComunicacion::ERROR_COMUNICACION ||
        protocolo.getEstado() == ProtocoloComunicacion::ERROR_TIMEOUT) {
        protocolo.reset();
    }
    
    cambiarEstado(ESTADO_RECIBIENDO);
}

void MaquinaEstado::iniciarEjecucion() {
    if (estadoMaquina != ESTADO_ESPERA && estadoMaquina != ESTADO_COMPLETADO) {
        Serial.println("[MAQUINA] Error: No se puede iniciar ejecución en estado actual");
        Serial.print("[MAQUINA] Estado actual: ");
        Serial.println(getEstadoTexto());
        Serial.println("[MAQUINA] Usa 's' para detener primero");
        return;
    }
    
    if (ejecutor.getComandoCount() == 0) {
        Serial.println("[MAQUINA] Error: No hay comandos cargados para ejecutar");
        Serial.println("[MAQUINA] Primero recibe datos con 'r'");
        return;
    }
    
    // Obtener los comandos actuales del ejecutor
    // Necesitamos copiarlos a comandosLocales para la ejecución secuencial
    int totalComandos = ejecutor.getComandoCount();
    for (int i = 0; i < totalComandos; i++) {
        // Necesitaríamos un método en EjecucionComandos para obtener comandos individuales
        // Por ahora, asumimos que ya están cargados en comandosLocales desde la recepción
    }
    comandoCountLocal = totalComandos;
    
    Serial.print("[MAQUINA] Iniciando ejecución de ");
    Serial.print(totalComandos);
    Serial.println(" comandos...");
    cambiarEstado(ESTADO_EJECUTANDO);
}

void MaquinaEstado::detenerEjecucion() {
    Serial.println("[MAQUINA] Deteniendo ejecución...");
    detenerComandoActual();
    ejecutor.detenerTodosLosComandos();
    cambiarEstado(ESTADO_ESPERA);
}

void MaquinaEstado::resetear() {
    Serial.println("[MAQUINA] Reset completo...");
    detenerComandoActual();
    ejecutor.detenerTodosLosComandos();
    protocolo.reset();
    
    comandoCountLocal = 0;
    indiceComandoActual = 0;
    comandoEnEjecucion = false;
    
    cambiarEstado(ESTADO_ESPERA);
}

String MaquinaEstado::getEstadoTexto() const {
    switch (estadoMaquina) {
        case ESTADO_INICIAL: return "INICIAL";
        case ESTADO_ESPERA: return "ESPERA";
        case ESTADO_RECIBIENDO: return "RECIBIENDO";
        case ESTADO_EJECUTANDO: return "EJECUTANDO";
        case ESTADO_COMPLETADO: return "COMPLETADO";
        case ESTADO_ERROR: return "ERROR";
        default: return "DESCONOCIDO";
    }
}

int MaquinaEstado::getComandosPendientes() const {
    if (estadoMaquina != ESTADO_EJECUTANDO) return 0;
    return ejecutor.getComandoCount() - indiceComandoActual;
}

MaquinaEstado::EstadoSistema MaquinaEstado::getEstadoCompleto() {
    EstadoSistema estado;
    
    estado.estadoMaquina = estadoMaquina;
    estado.estadoProtocolo = protocolo.getEstado();
    estado.comandosCargados = comandoCountLocal;
    estado.comandoActual = indiceComandoActual;
    estado.comandoActivo = comandoEnEjecucion;
    estado.estadoTextoMaquina = getEstadoTexto();
    estado.estadoTextoProtocolo = protocolo.getEstadoTexto();
    
    return estado;
}

void MaquinaEstado::ejecutarComandoDirecto(int actuador, int duracionMs) {
    if (actuador < 1 || actuador > 5) {
        Serial.println("[MAQUINA] Actuador inválido (1-5)");
        return;
    }
    
    Serial.print("[MAQUINA] Ejecutando comando directo: actuador ");
    Serial.print(actuador);
    Serial.print(" por ");
    Serial.print(duracionMs);
    Serial.println(" ms");
    
    // Crear comando simple
    int comando[5] = {1, actuador, 0, duracionMs, 0};
    
    // Ejecutar directamente
    digitalWrite(EjecucionComandos::getPinForActuador(actuador), HIGH);
    delay(duracionMs);
    digitalWrite(EjecucionComandos::getPinForActuador(actuador), LOW);
}