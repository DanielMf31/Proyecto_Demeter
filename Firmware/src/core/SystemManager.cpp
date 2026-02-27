#include "core/SystemManager.h"
#include <Arduino.h>

/**
 * @file SystemManager.cpp
 * @brief Orquestador del Workflow y Máquina de Estados Central.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * ¿Por qué existe un SystemManager si ya existe un ProtocolEngine?
 * 1. **Separación de Responsabilidades (SRP):** El ProtocolEngine sabe "cómo" 
 *    hablar (parsear bytes, checksums, tipos de tramas), pero el SystemManager 
 *    sabe "de qué" hablar y "cuándo". Gestionar reintentos, tiempos de espera 
 *    (timeouts) y el estado global (ej. BOOT vs RUNNING) es pura lógica de negocio.
 * 2. **Patrón Observer (Callbacks):** Mantiene desacoplados los componentes.
 *    El hardware avisa de un cambio de pin y el SystemManager reacciona,
 *    sin que el hardware tenga que importar librerías de red.
 */

// Constants for Handshake
const unsigned long HANDSHAKE_TIMEOUT_MS = 2000;
const uint8_t MAX_HANDSHAKE_ATTEMPTS = 3;

SystemManager::SystemManager(ProtocolEngine* engine) 
    : _engine(engine), _executor(nullptr), _sensorManager(nullptr), 
      _execMode(ExecutionMode::IMMEDIATE),
      _handshakeTargetId(0), _lastHandshakeActionTime(0), _handshakeAttempts(0),
      _sequenceStepIndex(0), _lastStepTime(0), _isSequencerActive(false) {}

void SystemManager::enableExecutor(GpioController* executor) {
    _executor = executor;
}

void SystemManager::enableSensorManager(SensorManager* manager) {
    _sensorManager = manager;
}

/**
 * @brief Configura el comportamiento base, inyecta dependencias al motor e inicializa el hardware.
 * 
 * ¿Por qué enganchamos los lambdas `[this]` al ProtocolEngine aquí?
 * Para hacer el "Bridge" entre la red y nuestra lógica. El motor disparará un
 * lambda cuando detecte una trama válida; ese lambda llamará a un método privado
 * como `handleGpioCommand`.
 */
void SystemManager::setup() {
    _context.setState(Demeter::SystemState::BOOT);
    
    if (_executor) {
        _executor->init();
    }
    
    if (_sensorManager) {
        _sensorManager->begin();
    }

    if (_engine) {
        // Sync Identity
        _engine->setNodeId(_context.nodeId());

        // Register Callbacks
        
        // GPIO
        _engine->onSetGpio([this](const Demeter::SetGpioCmd& cmd) {
            this->handleGpioCommand(cmd);
        });

        // Sequence
        _engine->onExecSequence([this](const Demeter::ExecSequenceCmd& cmd) {
            this->handleExecSequence(cmd);
        });

        // Handshake: SYN
        _engine->onSynRecv([this](const Demeter::AckData& data) {
            this->handleSynRecv(data);
        });

        // Handshake: SYN-ACK
        _engine->onSynAckRecv([this](const Demeter::AckData& data) {
            this->handleSynAckRecv(data);
        });

        // Handshake: ACK
        _engine->onAckRecv([this](const Demeter::AckData& data) {
            this->handleAckRecv(data);
        });

        // Data Reports
        _engine->onTempHumReportRecv([this](const Demeter::TempHumReport& report) {
            this->handleTempHumReport(report);
        });

        _engine->onPinReportRecv([this](const Demeter::PinReport& report) {
            this->handlePinReport(report);
        });

        _engine->onSystemReportRecv([this](const Demeter::SystemReport& report) {
            this->handleSystemReport(report);
        });
        
        // Requests
        _engine->onGetSensorsRecv([this](const Demeter::RequestData& req) {
             this->handleGetSensors(req);
        });

        _engine->onPingRecv([this](const Demeter::RequestData& req) {
            this->handlePing(req);
        });

        _engine->onRouteAddRecv([this](const Demeter::RouteAddCmd& cmd) {
            this->handleRouteAdd(cmd);
        });
    }

    // Entering IDLE state after successful boot
    _context.setState(Demeter::SystemState::IDLE);
    Serial.println(">> [System] Setup Complete. State: IDLE");
}

// =============================================================
// CALLBACKS EVENTOS
// =============================================================

void SystemManager::addAckListener(Demeter::AckCallback cb) {
    _ackListeners.push_back(cb);
}

void SystemManager::addGpioListener(Demeter::GpioCallback cb) {
    _gpioListeners.push_back(cb);
}

void SystemManager::addSequenceListener(Demeter::SequenceCallback cb) {
    _sequenceListeners.push_back(cb);
}

void SystemManager::addSensorDataListener(Demeter::TempHumReportCallback cb) {
    _sensorListeners.push_back(cb);
}

void SystemManager::addPinReportListener(Demeter::PinReportCallback cb) {
    _pinListeners.push_back(cb);
}

void SystemManager::addSystemReportListener(Demeter::SystemReportCallback cb) {
    _systemListeners.push_back(cb);
}

// =============================================================
// UPDATE
// =============================================================

/**
 * @brief Tick maestro de alta frecuencia.
 * 
 * ¿Por qué gestionamos el Sequencer y la Máquina de Estados de Handshake aquí?
 * Porque este método se llama continuamente desde el `loop()` iterativo principal.
 * Usando la diferencia entre el instante actual `millis()` y el momento en que 
 * se lanzó una acción `_lastStepTime`, evitamos detener el microcontrolador.
 * Si usáramos un `delay(1000)` para una secuencia, el ProtocolEngine se "quedaría 
 * sordo" durante ese segundo entero y se perderían paquetes.
 */
void SystemManager::update() {
    if (_context.getState() == Demeter::SystemState::ERROR) {
        return;
    }

    if (_engine) {
        _engine->update();
    }

    // State Machine
    switch (_context.getState()) {
        case Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK:
            runHandshakeLogic();
            break;
        
        case Demeter::SystemState::RUNNING:
        case Demeter::SystemState::IDLE:
            // Sequencer Logic (Only runs when "Connected/Running" or Idle)
            if (_isSequencerActive && !_activeSequence.empty() && _executor) {
                if (_sequenceStepIndex < _activeSequence.size()) {
                    unsigned long currentTime = millis();
                    // Check if the delay of the CURRENT step has passed
                    if (currentTime - _lastStepTime >= _activeSequence[_sequenceStepIndex].delayMs) {
                        // Move to next step
                        _sequenceStepIndex++;
                        
                        if (_sequenceStepIndex < _activeSequence.size()) {
                            // Execute NEXT Step
                            executeSequenceStep(_sequenceStepIndex);
                            _lastStepTime = currentTime;
                        } else {
                            Serial.println(">> [System] Sequence Execution Finished.");
                            _isSequencerActive = false;
                        }
                    }
                } else {
                     _isSequencerActive = false;
                }
            }
            break;
            
        default:
            break;
    }
}

// =============================================================
// HANDSHAKE LOGIC
// =============================================================

/**
 * @brief Detona un proceso de conexión segura en 3 Vías (3-Way Handshake TCP-like).
 * 
 * ¿Por qué simulamos un estado asíncrono en lugar de esperar la respuesta en línea?
 * En un sistema embebido Mono-Hilo interactuando con radios (ESP-NOW), "bloquearse" 
 * esperando la respuesta provocaría perder mensajes de otros nodos.
 * Marcamos el estado interno temporal a `HANDSHAKE_SEND_SYN` y dejamos que 
 * los ciclos sigan pasando hasta que recibamos la respuesta vía Callback.
 */
void SystemManager::initiateHandshake(uint8_t targetId, const Demeter::AckData& initialContext) {
    if (_context.getState() == Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK) return; // Already in progress

    _handshakeTargetId = targetId;
    _targetSessionContext = (Demeter::SessionContext)initialContext.context; 
    
    _handshakeAttempts = 0;
    _context.setState(Demeter::SystemState::HANDSHAKE_SEND_SYN);
    
    Serial.printf(">> [System] Initiating Handshake with Node %d (Context: 0x%02X)...\n", targetId, initialContext.context);
    
    // Send SYN immediately
    if (_engine) {
        Demeter::AckData synData = initialContext; // Copy
        _engine->sendSyn(_handshakeTargetId, synData);
        _lastHandshakeActionTime = millis();
        _context.setState(Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK);
    }
}

void SystemManager::runHandshakeLogic() {
    // Check Timeout
    if (millis() - _lastHandshakeActionTime > HANDSHAKE_TIMEOUT_MS) {
        _handshakeAttempts++;
        if (_handshakeAttempts >= MAX_HANDSHAKE_ATTEMPTS) {
            Serial.println(">> [System] Handshake Failed: Timeout.");
            _context.setState(Demeter::SystemState::IDLE); // Or ERROR
        } else {
            Serial.printf(">> [System] Handshake Retry %d...\n", _handshakeAttempts);
            Demeter::AckData synData = {0, 0};
            _engine->sendSyn(_handshakeTargetId, synData);
            _lastHandshakeActionTime = millis();
        }
    }
}

void SystemManager::handleSynRecv(const Demeter::AckData& data) {
    // Received SYN -> Send SYN-ACK
    Serial.printf(">> [System] RX SYN from %d. Sending SYN-ACK.\n", data.sourceId);
    if (_engine) {
        Demeter::AckData synAckData = {data.sourceId, 0}; // Target = Source of SYN
        _engine->sendSynAck(data.sourceId, synAckData);
    }
}

void SystemManager::handleAckRecv(const Demeter::AckData& data) {
    Serial.printf(">> [System] RX ACK from %d (Context: 0x%02X)\n", data.sourceId, data.context);
    
    if (data.context == (uint8_t)Demeter::SessionContext::SENSOR_REPORT) {
        Serial.println(">> [System] Node signaled SENSOR_REPORT session.");
    }

    // Notify Listeners
    for(const auto& cb : _ackListeners) cb(data);
}

void SystemManager::handleSynAckRecv(const Demeter::AckData& data) {
    if (_context.getState() == Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK && data.sourceId == _handshakeTargetId) {
        Serial.printf(">> [System] RX SYN-ACK from %d. Handshake Complete.\n", data.sourceId);
        
        // Send final ACK with Context
        if (_engine) {
            Demeter::AckData ackData = {0, (uint8_t)_targetSessionContext};
            _engine->sendAck(data.sourceId, ackData);
            Serial.printf(">> [System] Sent ACK with Context 0x%02X. Entering RUNNING state.\n", (uint8_t)_targetSessionContext);
        }
        
        _context.setState(Demeter::SystemState::RUNNING);
    }
}

// =============================================================
// COMMAND LOGIC IMPLEMENTATION
// =============================================================

/**
 * @brief Manejador inyectado ejecutado cuando la red nos manda cambiar un Pin.
 * 
 * Al separarlo, si en el futuro queremos que el pin parpadee o cambie paulatinamente (PWM),
 * solo modificamos esta función sin tocar la capa de red.
 */
void SystemManager::handleGpioCommand(const Demeter::SetGpioCmd& cmd) {
    if (_executor) {
        // Execute Immediately for now
        Demeter::SetGpioCmd command = cmd;
        _executor->execute(command);
        
        Serial.printf(">> [System] Executed GPIO Command: Pin %d -> %d\n", cmd.pin, cmd.value);
    }
}

void SystemManager::handleExecSequence(const Demeter::ExecSequenceCmd& cmd) {
    if (cmd.steps.empty()) return;
    
    _activeSequence = cmd.steps;
    _sequenceStepIndex = 0;
    _isSequencerActive = true;
    _lastStepTime = millis();
    
    Serial.printf(">> [System] Start Executing Sequence (%d steps)\n", (int)cmd.steps.size());
    
    // Execute Step 0 Immediately
    executeSequenceStep(0);
}

void SystemManager::executeSequenceStep(size_t index) {
    if (index >= _activeSequence.size()) return;
    const auto& step = _activeSequence[index];

    if (step.pin == 0) {
        Serial.printf(">> [Sequencer] Step %d: WAIT for %lu ms\n", (int)index, step.delayMs);
    } else {
        Serial.printf(">> [Sequencer] Step %d: PIN %d -> %s (Wait: %lu ms)\n", 
            (int)index, step.pin, step.value ? "ON" : "OFF", step.delayMs);
        
        if (_executor) {
            Demeter::SetGpioCmd gpioCmd;
            gpioCmd.pin = step.pin;
            gpioCmd.value = step.value;
            gpioCmd.flags = 0;
            _executor->execute(gpioCmd);
        }
    }
}


// =============================================================
// CENTRALIZED DATA HANDLERS (Implementation)
// =============================================================

void SystemManager::handleTempHumReport(const Demeter::TempHumReport& report) {
    // Notify Listeners
    for(const auto& cb : _sensorListeners) cb(report);
}

void SystemManager::handlePinReport(const Demeter::PinReport& report) {
    // Notify Listeners
    for(const auto& cb : _pinListeners) cb(report);
}

void SystemManager::handleSystemReport(const Demeter::SystemReport& report) {
    // Notify Listeners
    for(const auto& cb : _systemListeners) cb(report);
}

void SystemManager::handlePing(const Demeter::RequestData& req) {
    // Manually send ACK
    if (_engine) {
        Demeter::AckData ack = {req.sourceId, 0};
        _engine->sendAck(req.sourceId, ack);
    }
}

void SystemManager::handleRouteAdd(const Demeter::RouteAddCmd& cmd) {
    if (_engine) {
        _engine->registerRoute(cmd.nodeId, cmd.mac);
        // Manually ACK the configuration
        Demeter::AckData ack = {cmd.nodeId, 0}; 
        _engine->sendAck(cmd.nodeId, ack);
    }
}

void SystemManager::handleGetSensors(const Demeter::RequestData& req) {
    // Auto-respond if we are a Sensor Node
    if (_sensorManager) {
        auto readings = _sensorManager->readAll();
        for (const auto& r : readings) {
            Demeter::TempHumReport report = {0, r.value1, r.value2};
            sendSensorData(req.sourceId, report);
        }
    }
}

// =============================================================
// CENTRALIZED COMPOSERS (Implementation)
// =============================================================

void SystemManager::sendSensorData(uint8_t targetId, const Demeter::TempHumReport& report) {
    if (_engine) {
        _engine->sendTempHumReport(targetId, report);
    }
}

void SystemManager::sendPinStatus(uint8_t targetId, const Demeter::PinReport& report) {
    if (_engine) {
        _engine->sendPinReport(targetId, report);
    }
}

void SystemManager::sendSystemStatus(uint8_t targetId, const Demeter::SystemReport& report) {
    if (_engine) {
        _engine->sendSystemReport(targetId, report);
    }
}

/**
 * @brief Agrupa las métricas estáticas leídas de cada cable hardware empaquetándolas.
 * 
 * ¿Por qué MOCK_DATA_ENABLED? 
 * Durante el desarrollo frontend/backend a veces la parte electrónica del sensor real
 * no está montada en la protoboard. Enchufando este flag generamos varianza 
 * pseudoaleatoria para testear los gráficos de grafana y la Base de Datos.
 */
void SystemManager::collectAndPublishSensorData(uint8_t targetId) {
    if (!_sensorManager) return;

#if defined(MOCK_DATA_ENABLED) || defined(USE_MOCK_SENSORS)
    // MOCK DATA IMPLEMENTATION (Requested by User)
    Demeter::TempHumReport mockReport;
    mockReport.sourceId = _context.nodeId();
    // Simulate varying data
    mockReport.temperature = 20.0f + (rand() % 100) / 10.0f; // 20.0 - 30.0
    mockReport.humidity = 50.0f + (rand() % 200) / 10.0f;    // 50.0 - 70.0
    
    sendSensorData(targetId, mockReport);
    Serial.printf("[SystemManager] Published MOCK Data to Node %d: %.2f C, %.2f %%\n", targetId, mockReport.temperature, mockReport.humidity);
#else
    // REAL SENSOR DATA
    auto readings = _sensorManager->readAll();
    for (const auto& data : readings) {
       Demeter::TempHumReport report;
       report.sourceId = _context.nodeId();
       report.temperature = data.value1;
       report.humidity = data.value2;
       
       sendSensorData(targetId, report);
    }
#endif
}

void SystemManager::requestSensors(uint8_t targetId, const Demeter::RequestData& req) {
    if (_engine) {
        _engine->sendGetSensors(targetId, req);
    }
}

void SystemManager::sendCommand(uint8_t targetId, const Demeter::SetGpioCmd& cmd) {
    if (_engine) {
        _engine->sendSetGpio(targetId, cmd);
    }
}

void SystemManager::injectCommand(const Demeter::SetGpioCmd& cmd) {
    // Directly execute command via internal handler
    handleGpioCommand(cmd);
}
