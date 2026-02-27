#pragma once

#include "core/INode.h"
#include "core/ProtocolEngine.h"
#include "core/SystemManager.h"
#include "core/SensorManager.h"

/**
 * @class Node_Sensor
 * @brief Implementación concreta de Nodo para perfiles estrictamente de Sensor.
 * 
 * Especialización de la interfaz INode para dispositivos de telemetría.
 * Gestiona explícitamente el SensorManager, el ProtocolEngine y el SystemManager.
 * Emite reportes aéreos tras iterar la lectura del pool de sensores.
 * 
 * @par Ejemplo de uso (Setup Principal):
 * @code
 * ProtocolEngine engine(&comms);
 * Node_Sensor sensorNode(DEVICE_ID, &engine);
 * sensorNode.setReportingConfig(60000, true); // Reporte mensual de 1 min con sleep
 * sensorNode.getSensorManager()->addSensor(new MockSensor());
 * sensorNode.begin();
 * 
 * void loop() { sensorNode.update(); }
 * @endcode
 */
class Node_Sensor : public INode {
private:
    uint8_t _nodeId;
    ProtocolEngine* _engine;
    SystemManager* _systemManager;
    SensorManager* _sensorManager;
    
    // Reporting Config
    uint32_t _reportIntervalMs;
    unsigned long _lastReportTime;
    bool _deepSleepEnabled;

    /**
     * @brief Tarea Ticking que itera los sensores, recaba la info y se la envía al Protocol Engine.
     */
    void collectAndSend();

public:
    /**
     * @brief Instancia un contenedor Node Sensor Típico.
     * @param id ID único físico/lógico del nodo.
     * @param engine Puntero a la instancia activa del motor de protocolo (serializador + routing).
     */
    Node_Sensor(uint8_t id, ProtocolEngine* engine);
    ~Node_Sensor();

    /** @brief Arranca los subsistemas hardware y máquinas de estado en init. */
    void begin() override;
    
    /** @brief Tarea a correr ininterrumpidamente en el `loop()` de Arduino. */
    void update() override;

    /**
     * @brief Configura el comportamiento de reportería.
     * @param intervalMs Tiempo entre reportes aéreos de telemetría (0 = Solo On Demand).
     * @param deepSleep true para entrar a Deep Sleep entre dichos reportes, minimizando batería.
     */
    void setReportingConfig(uint32_t intervalMs, bool deepSleep);

    /** @return Instancia del gestor de sensores de hardware para vincular punteros DHT/I2C. */
    SensorManager* getSensorManager() { return _sensorManager; }
    
    /** @return Gestor de estado para callbacks asíncronos o manejo de deep sleep explícito. */
    SystemManager* getSystemManager() { return _systemManager; }
};
