/**
 * @file Node_Sensor.cpp
 * @brief Firmware lógico para el Nodo Extremo de tipo Sensor.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Por qué aislar la lógica Sensórica en una clase concreta (Herencia de INode)?**
 *    Porque un Nodo Sensor tiene un ciclo de vida fundamentalmente diferente a un
 *    Actuador o Gateway. Este nodo debe dormir profusamente (Deep Sleep) para
 *    ahorrar batería (es de borde lejano).
 * 2. **Desacoplamiento del Hardware Específico:** Observa que no instanciamos un
 *    sensor DHT o I2C directamente aquí. Este nodo tiene un objeto genérico 
 *    `SensorManager`. Al componerlo de este gestor abstracto, esta clase sirve para
 *    **cualquier** combinación de sensores atmosféricos que hagamos.
 */

#include "core/Node_Sensor.h"
#include <Arduino.h>

/**
 * @brief Constructor. Instancia el nodo lógico e inyecta la comunicación.
 * 
 * Por qué el motor ProtocolEngine llega desde fuera (inyección de dependencias) 
 * y no se crea aquí dentro?
 * - Porque este nodo lógico no debe saber, ni debería interesarle, cómo se 
 *   manda físicamente el byte aéreo (si es UART, Lora o ESPNOW). Este nivel 
 *   de indirección facilita testeo.
 */
Node_Sensor::Node_Sensor(uint8_t id, ProtocolEngine* engine) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr),
      _sensorManager(new SensorManager()), 
      _reportIntervalMs(0), _lastReportTime(0), _deepSleepEnabled(false) {
    
    // Dependency Injection into SystemManager
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        // Enable SensorManager in SystemManager
        if (_sensorManager) {
            _systemManager->enableSensorManager(_sensorManager);
        }
    }
}

Node_Sensor::~Node_Sensor() {
    if (_sensorManager) {
        delete _sensorManager;
    }
    if (_systemManager) {
        delete _systemManager;
    }
}

/**
 * @brief Rutina de arranque desvinculada del constructor.
 * 
 * ¿Por qué en un método a parte?
 * Porque el entorno de hardware del ESP32 está inmaduro hasta que la función
 * setup() general de esp-idf arranca. Si registráramos callbacks serie en el
 * constructor global provocaríamos Exception Panels.
 */
void Node_Sensor::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context - Define qué sabe de sí mismo en RAM.
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::SENSOR);
    ctx.setConfig(_reportIntervalMs, _deepSleepEnabled);

    // 2. Initialize SystemManager (Handles callbacks automatically).
    // Delega al orquestador central (SystemManager) decirle a cada módulo hardware
    // subyacente (.begin()) que se inicialice de forma segura.
    _systemManager->setup();

    Serial.println("[Node_Sensor] Initialized.");
}

/**
 * @brief Tic central del dispositivo inyectado en el loop infinito.
 * 
 * En vez de ensuciar el C++ puro con esperas de IO, se utiliza explícitamente 
 * el patrón "Máquina de Estados de ejecución periódica". Dependiendo del estado
 * interno se actúa distinto en cada milisegundo. Esto nos evita `delay(X)`
 * que mata la responsividad a la recepción de eventos remotos.
 */
void Node_Sensor::update() {
    // 1. Drenar I/O. Siempre se debe permitir al SystemManager 
    // decodificar en su Engine los paquetes que hayan encallado en HW.
    if (_systemManager) {
        _systemManager->update();
    } else {
        return; 
    }

    // 2. Lógica de alto nivel (Software Control)
    Demeter::SystemState state = _systemManager->getState();

    switch (state) {
        case Demeter::SystemState::BOOT:
        case Demeter::SystemState::IDLE:
        case Demeter::SystemState::ERROR:
            // ¿Por qué hacemos Handshake continuo si no estamos conectados?
            // "Disponibilidad Eventual". Si la red está cortada nos interesa
            // intentarlo esporádicamente para readherirse a la estrucutura mesh.
            static unsigned long lastConnectAttempt = 0;
            if (millis() - lastConnectAttempt > 5000) {
                 Serial.println("[Node_Sensor] State is IDLE/BOOT. Initiating Handshake with Server (0)...");
                 Demeter::AckData context = {0, (uint8_t)Demeter::SessionContext::SENSOR_REPORT};
                 _systemManager->initiateHandshake(0, context); // Handshake with Server (0)
                 lastConnectAttempt = millis();
            }
            break;

        case Demeter::SystemState::HANDSHAKE_SEND_SYN:
        case Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK:
        case Demeter::SystemState::HANDSHAKE_SEND_ACK: // Transiciones efímeras, saltamos.
            break;

        case Demeter::SystemState::RUNNING:
            // 3. Connected! Disparo del Reporte Automático por umbral de tiempo.
            // Si el modo configurado es Activo (timer), delegamos al orquestador general
            // extraer info concreta porque el SensorNode en sí desconoce a bajo 
            // nivel qué tipo de sensores tiene enganchados.
            if (_reportIntervalMs > 0) {
                if (millis() - _lastReportTime >= _reportIntervalMs) {
                    _systemManager->collectAndPublishSensorData(0); // Target Server (0) via Gateway
                    _lastReportTime = millis();

                    if (_deepSleepEnabled) {
                        // En sistemas remotos y alimentados con placas solares o
                        // power-banks, el Deep Sleep baja consumos de ~120mA a ~15uA.
                        Serial.println("[Node_Sensor] Going to Sleep...");
                        Serial.flush(); // Imparativo para que el UART no colapse por corte de energía.
                        // esp_deep_sleep(_reportIntervalMs * 1000);
                    }
                }
            }
            break;
    }
}

void Node_Sensor::collectAndSend() {
    // Deprecated. Use _systemManager->collectAndPublishSensorData(0) directly
    if (_systemManager) _systemManager->collectAndPublishSensorData(0);
}

void Node_Sensor::setReportingConfig(uint32_t intervalMs, bool deepSleep) {
    _reportIntervalMs = intervalMs;
    _deepSleepEnabled = deepSleep;
}
