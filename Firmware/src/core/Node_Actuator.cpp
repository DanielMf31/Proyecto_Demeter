/**
 * @file Node_Actuator.cpp
 * @brief Implementación de la Lógica del Nodo Acutador y su Máquina de Estados.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Composición de Hardware:** Un `Node_Actuator` inyecta dependencias hacia el
 *    `GpioController`. A diferencia del SensorNode, no duerme, porque debe estar
 *    perennemente escuchando la red (esperando directrices de activación).
 * 2. **Delegación de Control:** El actuador no sabe qué protocolo usa. Solo dice:
 *    "Cuando llegue un comando GPIO válido por la red, SystemManager avísame
 *    con este Callback".
 */
#include "core/Node_Actuator.h"
#include <Arduino.h>

/**
 * @brief Constructor del Nodo Actuador.
 * 
 * ¿Por qué el SystemManager y GpioController se orquestan aquí dentro?
 * - `GpioController` puede venir de fuera (dependencia mockeada para tests) o instanciarse
 *   por default.
 * - `SystemManager` requiere una referencia fuerte a `ProtocolEngine` (que viene de afuera).
 *   Si logramos instanciar el cerebro, enlazamos las interfaces hardware con `.enable*()`.
 */
Node_Actuator::Node_Actuator(uint8_t id, ProtocolEngine* engine, GpioController* executor) 
    : _nodeId(id), _engine(engine), _systemManager(nullptr), 
      _executor(executor ? executor : new GpioController()) {
    
    if (_engine) {
        _systemManager = new SystemManager(_engine);
        // Habilita explícitamente el actuador en la pasarela lógica.
        if (_executor) {
            _systemManager->enableExecutor(_executor);
        }
    }
}

Node_Actuator::~Node_Actuator() {
    if (_executor) {
        delete _executor;
    }
    if (_systemManager) {
        delete _systemManager;
    }
}

/**
 * @brief Arranque de las subestructuras que dependen de las apis reales del MCU.
 * 
 * ¿Por qué esta función está separada del loop e init principal?
 * Permite que un `main_*.cpp` reconfigure la variable `_nodeId` o altere los pines 
 * en `_executor` ANTES de que el `SystemManager` corra `.setup()` e ingrese a un
 * modo donde los pines queden boicoteados.
 */
void Node_Actuator::begin() {
    if (!_systemManager) return;

    // 1. Initialize Context
    auto& ctx = _systemManager->getContext();
    ctx.setIdentity(_nodeId, Demeter::NodeRole::ACTUATOR);

    // 2. Initialize SystemManager
    _systemManager->setup();

    // 3. Skip handshake — go straight to RUNNING so we can receive commands
    //    immediately. In local/edge mode there is no server to handshake with.
    ctx.setState(Demeter::SystemState::RUNNING);

    Serial.println("[Node_Actuator] Initialized (RUNNING, no handshake).");
}

/**
 * @brief Tick repetitivo sin demoras (Non-blocking loop).
 * 
 * ¿Por qué no encapsulamos todo el Handshake dentro del ProtocolEngine?
 * El `ProtocolEngine` solo decodifica bytes y valida checksums (Responsabilidad Única).
 * La "intención" del dispositivo de conectarse o de reintentar una conexión fallida,
 * depende de la aplicación de usuario, o sea, de la Máquina de Estados controlada
 * aquí y gobernada por `SystemManager`.
 */
void Node_Actuator::update() {
    // 1. Update System Manager (vaciar y enrutar buzón de red)
    if (_systemManager) {
        _systemManager->update();
    } else {
        return;
    }

    // 2. State Machine evaluation
    Demeter::SystemState state = _systemManager->getState();

    switch (state) {
        case Demeter::SystemState::BOOT:
        case Demeter::SystemState::IDLE:
        case Demeter::SystemState::ERROR:
            // No auto-handshake: in local/edge mode there is no server.
            // The node stays in RUNNING (set in begin()) and listens for commands.
            break;

        case Demeter::SystemState::HANDSHAKE_SEND_SYN:
        case Demeter::SystemState::HANDSHAKE_WAIT_SYN_ACK:
        case Demeter::SystemState::HANDSHAKE_SEND_ACK:
            break;

        case Demeter::SystemState::RUNNING:
            // Actuator is passive: espera comandos via callbacks configuradas en el setup.
            break;
    }
}

void Node_Actuator::addGpioListener(Demeter::GpioCallback cb) {
    if (_systemManager) {
        _systemManager->addGpioListener(cb);
    }
}
