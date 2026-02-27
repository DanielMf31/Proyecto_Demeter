#pragma once

#include "core/ProtocolEngine.h"
#include "core/GpioController.h"
#include "core/SensorManager.h"
#include "core/InternalTypes.h"
#include "core/SystemContext.h"
#include <vector>

// System States
// System States moved to InternalTypes.h (Demeter::SystemState)

/**
 * @brief Modalidad de Ejecución de Comandos del Sistema.
 * @note Actualmente soportado mayoritariamente el IMMEDIATE.
 */
enum class ExecutionMode {
    IMMEDIATE,         ///< Ejecutar tan pronto como el comando se decodifice e identifique (Defecto).
    INTERACTIVE_QUEUE  ///< Encolar comandos temporalmente; ejecutar luego por un trigger programado.
};

/**
 * @class SystemManager
 * @brief Cerebro y Máquina de Estados del Firmware Demeter.
 *
 * Implementa el flujo de control centralizado (Workflow Controller) cruzando las fronteras entre:
 * - Protocol Engine (Comunicaciones e Input/Output Serializado)
 * - GpioController / SensorManager (Hardware Físico subyacente)
 * - Lógica Transaccional (Handshake 3-vías, Sesiones de ACK).
 * 
 * @par Ejemplo de uso:
 * @code
 * SystemManager sys(&protocolEngine);
 * sys.enableExecutor(&gpioCtrl);
 * sys.setup();
 * sys.initiateHandshake(GATEWAY_ID, SessionContext::GENERAL);
 * 
 * void loop() { sys.update(); } // Mantener vivo
 * @endcode
 */
class SystemManager {
private:
    ProtocolEngine* _engine;
    GpioController* _executor; // Optional (Actuator Node only)
    SensorManager* _sensorManager; // Optional (Sensor Node only)
    
    Demeter::SystemContext _context;
    ExecutionMode _execMode;

    // Handshake Variables
    uint8_t _handshakeTargetId; // Logic variable, keep here
    unsigned long _lastHandshakeActionTime;
    uint8_t _handshakeAttempts;

    // Command Queue for Interactive Mode
    std::vector<Demeter::SetGpioCmd> _commandQueue;

    // Sequencer State
    std::vector<Demeter::SequenceStep> _activeSequence;
    size_t _sequenceStepIndex;
    unsigned long _lastStepTime;
    bool _isSequencerActive;

    // Listeners for Chain of Responsibility
    std::vector<Demeter::GpioCallback> _gpioListeners;
    std::vector<Demeter::SequenceCallback> _sequenceListeners;
    std::vector<Demeter::TempHumReportCallback> _sensorListeners;
    std::vector<Demeter::PinReportCallback> _pinListeners;
    std::vector<Demeter::SystemReportCallback> _systemListeners;
    std::vector<Demeter::AckCallback> _ackListeners;

    // Internal Callback
    void handleGpioCommand(const Demeter::SetGpioCmd& cmd);
    void handleSynRecv(const Demeter::AckData& data);
    void handleSynAckRecv(const Demeter::AckData& data);
    void handleAckRecv(const Demeter::AckData& data);
    
    // Data Handlers (Standardized)
    void handleTempHumReport(const Demeter::TempHumReport& report);
    void handlePinReport(const Demeter::PinReport& report);
    void handleSystemReport(const Demeter::SystemReport& report);
    void handleGetSensors(const Demeter::RequestData& req);

    // Context
    Demeter::SessionContext _targetSessionContext;

    // Protocol Logic
    void runHandshakeLogic();

    // Sequencer Helper
    void executeSequenceStep(size_t index);

public:
    /**
     * @brief Construct a new System Manager.
     * @param engine Pointer to Protocol Engine.
     */
    SystemManager(ProtocolEngine* engine);


    /**
     * @brief Enable the Executor Module.
     * @param executor Pointer to GpioController.
     */
    void enableExecutor(GpioController* executor);

    /**
     * @brief Enable the Sensor Manager Module.
     * @param manager Pointer to SensorManager.
     */
    void enableSensorManager(SensorManager* manager);

    GpioController* getExecutor() const { return _executor; }
    SensorManager* getSensorManager() const { return _sensorManager; }
    ProtocolEngine* getProtocolEngine() const { return _engine; }

    /**
     * @brief Initialize the system components.
     * Sets up callbacks and initializes enabled hardware.
     */
    void setup();

    /**
     * @brief Bucle Principal del Sistema (Tick OBLIGATORIO).
     * @note Se debe invocar perennemente dentro del `loop()` de la placa.
     * 
     * Responsabilidades asumidas:
     * - Avance máquina Protocol Engine.
     * - Evaluación timeout `HANDSHAKE`.
     * - Iteración automática de Pasos de Secuenciador (`ExecSequenceCmd`).
     * - Procesamiento de transacciones diferidas.
     */
    void update();

    // --- Actions ---


    /**
     * @brief Initiate a Handshake with a target node.
     * @param targetId The ID of the node to connect to.
     * @param initialContext The intent/session type (wrapped in AckData).
     */
    void initiateHandshake(uint8_t targetId, const Demeter::AckData& initialContext = {0, 0});

    // --- Centralized Senders ---
    void sendSensorData(uint8_t targetId, const Demeter::TempHumReport& report);
    void sendPinStatus(uint8_t targetId, const Demeter::PinReport& report);
    void sendSystemStatus(uint8_t targetId, const Demeter::SystemReport& report);
    void requestSensors(uint8_t targetId, const Demeter::RequestData& req);
    void sendCommand(uint8_t targetId, const Demeter::SetGpioCmd& cmd);
    
    /**
     * @brief Collects data from SensorManager and publishes it.
     * @param targetId Gateway ID (usually 1).
     */
    void collectAndPublishSensorData(uint8_t targetId);

    void setExecutionMode(ExecutionMode mode);
    void executeQueue();
    void clearQueue();
    
    // Public Handler for Protocol
    void handleExecSequence(const Demeter::ExecSequenceCmd& cmd);
    void handleRouteAdd(const Demeter::RouteAddCmd& cmd);
    void handlePing(const Demeter::RequestData& req);

    // Manual Command Injection
    void injectCommand(const Demeter::SetGpioCmd& cmd);

    // Listener Registration
    void addGpioListener(Demeter::GpioCallback cb);
    void addSequenceListener(Demeter::SequenceCallback cb);
    void addSensorDataListener(Demeter::TempHumReportCallback cb);
    void addPinReportListener(Demeter::PinReportCallback cb);
    void addSystemReportListener(Demeter::SystemReportCallback cb);
    void addAckListener(Demeter::AckCallback cb);

    // Context
    Demeter::SystemContext& getContext() { return _context; }
    Demeter::SystemState getState() const { return _context.getState(); }
};
