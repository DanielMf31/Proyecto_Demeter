#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/GpioController.h"

/**
 * @class Node_Actuator
 * @brief Implementación concreta de Nodo para perfiles estrictamente Actuadores.
 * 
 * Nodo dependiente de corriente de red contínua (Power-plugged) que escucha 
 * constantemente requerimientos para modificar salidas GPIO hardware (Relés o PWM).
 * Acopla las peticiones entrantes del Protocol Engine al Executor de GPIO.
 * 
 * @par Ejemplo de uso:
 * @code
 * GpioController myExecutor;
 * ProtocolEngine engine(&comms);
 * Node_Actuator actNode(DEVICE_ID, &engine, &myExecutor);
 * actNode.begin();
 * @endcode
 */
class Node_Actuator : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    GpioController* _executor;

public:
    /**
     * @brief Construye el rol Actuador.
     * @param id ID unívoco lógico.
     * @param engine Motor de serialización CBOR vinculado a un puerto de Comms.
     * @param executor Instancia oída encargada de interactuar con hardware IO.
     */
    Node_Actuator(uint8_t id, ProtocolEngine* engine, GpioController* executor = nullptr);
    ~Node_Actuator();

    /** @brief Inicializa los controladores hardware subyacentes. */
    void begin() override;
    
    /** @brief Tick regular ligado al firmware Arduino `loop`. */
    void update() override;
    
    /**
     * @brief Registra callbacks extra reactivos ante una modificación GPIO.
     * Facade a `ProtocolEngine::onSetGpioCommand`.
     * @param cb Callback C++ de la firma `std::function<void(const SetGpioCmd&)>`.
     */
    void addGpioListener(Demeter::GpioCallback cb);
    
    /** @return Puntero de acceso al ejecutor físico, usado habitualmente en el setup(). */
    GpioController* getExecutor() { return _executor; }
    
    /** @return Gestor de estado del sistema (batería, flags). */
    SystemManager* getSystemManager() { return _systemManager; }
};
