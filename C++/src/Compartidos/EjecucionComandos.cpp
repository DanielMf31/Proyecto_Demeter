#include "EjecucionComandos.h"

EjecucionComandos::EjecucionComandos() : comandoCount(0) {
    // Configurar pines de actuadores
    pinMode(PIN_A1, OUTPUT);
    pinMode(PIN_A2, OUTPUT);
    pinMode(PIN_A3, OUTPUT);
    pinMode(PIN_A4, OUTPUT);
    pinMode(PIN_A5, OUTPUT);
    
    // Asegurar que todos empiecen apagados
    digitalWrite(PIN_A1, LOW);
    digitalWrite(PIN_A2, LOW);
    digitalWrite(PIN_A3, LOW);
    digitalWrite(PIN_A4, LOW);
    digitalWrite(PIN_A5, LOW);
    
    Serial.println("[EJECUTOR] Inicializado - Pines 4-8 configurados");
}

void EjecucionComandos::cargarComandosDesdeArray(int comandosExternos[100][5], int count) {
    if (count <= 0 || count > 100) return;
    
    // Detener todos los comandos actuales
    detenerTodosLosComandos();
    
    // Copiar comandos
    comandoCount = count;
    for (int i = 0; i < count; i++) {
        for (int j = 0; j < 5; j++) {
            comandosLocales[i][j] = comandosExternos[i][j];
        }
        comandoActivo[i] = false;
        tiemposInicio[i] = 0;
    }
    
    Serial.print("[EJECUTOR] Cargados ");
    Serial.print(count);
    Serial.println(" comandos");
}

void EjecucionComandos::anadirComando(int tipo, int actuador, int parametro, int duracion, int reservado) {
    if (comandoCount >= 100) return;
    
    comandosLocales[comandoCount][0] = tipo;
    comandosLocales[comandoCount][1] = actuador;
    comandosLocales[comandoCount][2] = parametro;
    comandosLocales[comandoCount][3] = duracion;
    comandosLocales[comandoCount][4] = reservado;
    
    comandoActivo[comandoCount] = false;
    tiemposInicio[comandoCount] = 0;
    
    comandoCount++;
    
    Serial.print("[EJECUTOR] Comando añadido #");
    Serial.print(comandoCount);
    Serial.print(": A");
    Serial.print(actuador);
    Serial.print(" por ");
    Serial.print(duracion);
    Serial.println("ms");
}

void EjecucionComandos::ejecutarComando(int idx) {
    if (idx < 0 || idx >= comandoCount) return;
    if (comandoActivo[idx]) return;
    
    int actuador = comandosLocales[idx][1];
    int duracion = comandosLocales[idx][3];
    
    if (actuador < 1 || actuador > 5) return;
    
    // Activar el pin
    switch(actuador) {
        case 1: digitalWrite(PIN_A1, HIGH); break;
        case 2: digitalWrite(PIN_A2, HIGH); break;
        case 3: digitalWrite(PIN_A3, HIGH); break;
        case 4: digitalWrite(PIN_A4, HIGH); break;
        case 5: digitalWrite(PIN_A5, HIGH); break;
    }
    
    // Marcar como activo
    comandoActivo[idx] = true;
    tiemposInicio[idx] = millis();
    
    Serial.print("[EJECUTOR] ▶ Cmd ");
    Serial.print(idx);
    Serial.print(": A");
    Serial.print(actuador);
    Serial.print(" ON por ");
    Serial.print(duracion);
    Serial.println("ms");
}

void EjecucionComandos::detenerComando(int idx) {
    if (idx < 0 || idx >= comandoCount) return;
    if (!comandoActivo[idx]) return;
    
    int actuador = comandosLocales[idx][1];
    
    // Desactivar el pin
    switch(actuador) {
        case 1: digitalWrite(PIN_A1, LOW); break;
        case 2: digitalWrite(PIN_A2, LOW); break;
        case 3: digitalWrite(PIN_A3, LOW); break;
        case 4: digitalWrite(PIN_A4, LOW); break;
        case 5: digitalWrite(PIN_A5, LOW); break;
    }
    
    comandoActivo[idx] = false;
    
    unsigned long tiempoEjecutado = millis() - tiemposInicio[idx];
    Serial.print("[EJECUTOR] ✓ Cmd ");
    Serial.print(idx);
    Serial.print(": A");
    Serial.print(actuador);
    Serial.print(" OFF (");
    Serial.print(tiempoEjecutado);
    Serial.println("ms)");
}

void EjecucionComandos::detenerTodosLosComandos() {
    for (int i = 0; i < comandoCount; i++) {
        if (comandoActivo[i]) {
            detenerComando(i);
        }
    }
    
    // También apagar todos los pines
    digitalWrite(PIN_A1, LOW);
    digitalWrite(PIN_A2, LOW);
    digitalWrite(PIN_A3, LOW);
    digitalWrite(PIN_A4, LOW);
    digitalWrite(PIN_A5, LOW);
}

bool EjecucionComandos::estaActivo(int idx) {
    if (idx < 0 || idx >= comandoCount) return false;
    return comandoActivo[idx];
}

bool EjecucionComandos::haCompletadoDuracion(int idx) {
    if (idx < 0 || idx >= comandoCount) return false;
    if (!comandoActivo[idx]) return false;
    
    int duracion = comandosLocales[idx][3];
    if (duracion == 0) return false; // Comando continuo
    
    unsigned long tiempoTranscurrido = millis() - tiemposInicio[idx];
    return (tiempoTranscurrido >= duracion);
}

void EjecucionComandos::verificarCompletados() {
    for (int i = 0; i < comandoCount; i++) {
        if (comandoActivo[i] && haCompletadoDuracion(i)) {
            detenerComando(i);
        }
    }
}

void EjecucionComandos::mostrarComandosLocales() {
    if (comandoCount == 0) {
        Serial.println("[EJECUTOR] No hay comandos");
        return;
    }
    
    Serial.println("\n=== COMANDOS GUARDADOS ===");
    for (int i = 0; i < comandoCount; i++) {
        Serial.print(i);
        Serial.print(": [");
        Serial.print(comandosLocales[i][0]);
        Serial.print(",");
        Serial.print(comandosLocales[i][1]);
        Serial.print(",");
        Serial.print(comandosLocales[i][2]);
        Serial.print(",");
        Serial.print(comandosLocales[i][3]);
        Serial.print(",");
        Serial.print(comandosLocales[i][4]);
        Serial.print("] ");
        Serial.println(comandoActivo[i] ? "ACTIVO" : "INACTIVO");
    }
    Serial.println("==========================");
}

void EjecucionComandos::pruebaActuadores() {
    Serial.println("\n=== PRUEBA ACTUADORES ===");
    for (int i = 1; i <= 5; i++) {
        Serial.print("A");
        Serial.print(i);
        Serial.println(" ON");
        
        switch(i) {
            case 1: digitalWrite(PIN_A1, HIGH); break;
            case 2: digitalWrite(PIN_A2, HIGH); break;
            case 3: digitalWrite(PIN_A3, HIGH); break;
            case 4: digitalWrite(PIN_A4, HIGH); break;
            case 5: digitalWrite(PIN_A5, HIGH); break;
        }
        
        delay(1000);
        
        Serial.print("A");
        Serial.print(i);
        Serial.println(" OFF");
        
        switch(i) {
            case 1: digitalWrite(PIN_A1, LOW); break;
            case 2: digitalWrite(PIN_A2, LOW); break;
            case 3: digitalWrite(PIN_A3, LOW); break;
            case 4: digitalWrite(PIN_A4, LOW); break;
            case 5: digitalWrite(PIN_A5, LOW); break;
        }
        
        delay(500);
    }
    Serial.println("Prueba completada\n");
}

void EjecucionComandos::limpiarComandos() {
    detenerTodosLosComandos();
    comandoCount = 0;
    Serial.println("[EJECUTOR] Comandos limpiados");
}