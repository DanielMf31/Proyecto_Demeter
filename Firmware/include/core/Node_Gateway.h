#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/GpioController.h"
#include "core/SensorManager.h"

/**
 * @class Node_Gateway
 * @brief Especialización de Hardware híbrida que funciona como Concentrador.
 * 
 * Este nodo recolecta mensajes de la red de área local (ej. ESP-NOW), 
 * los transmite a una topología superior (ej. vía UART a una Raspberry Pi)
 * y además puede poseer lógicas de sensor/actuador local embebidas.
 * 
 * @par Ejemplo de uso:
 * @code
 * ProtocolEngine engine(&commsEdge);
 * Node_Gateway gwNode(GATEWAY_ID, &engine);
 * gwNode.begin();
 * 
 * void loop() { gwNode.update(); }
 * @endcode
 */
class Node_Gateway : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    GpioController* _executor;
    SensorManager* _sensorManager;

public:
    /**
     * @brief Construye el rol Gateway.
     * @param id ID unívoco lógico del Gateway central (suelen ser el ID 1).
     * @param engine Motor asociado a las interfaces de bajada (edge) y subida (uplink).
     */
    Node_Gateway(uint8_t id, ProtocolEngine* engine);
    ~Node_Gateway();

    /** @brief Arranca los administradores de sensores, pines y la máquina de estados. */
    void begin() override;
    
    /** @brief Tarea regular Arduino loop() delegada hacia SystemManager. */
    void update() override;

    // Accessors for hybrid capabilities
    
    /** @return Capacidad para interactuar con GPIO propio de la GW. */
    GpioController* getExecutor() { return _executor; }
    
    /** @return Capacidad para medir telemetría propia de la GW. */
    SensorManager* getSensorManager() { return _sensorManager; }
    
    /** @return Motor central de estados de la GW. */
    SystemManager* getSystemManager() { return _systemManager; }
};
