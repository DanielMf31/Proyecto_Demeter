#pragma once

#include "hardware/ISensor.h"
#include <vector>
#include <memory>

/**
 * @class SensorManager
 * @brief Agrupa y orquesta una colección heterogénea de sensores de Hardware.
 * 
 * Permite que nodos complejos tengan `N` sensores independientes. Centraliza
 * el proceso de muestreo devolviendo un vector curado de lecturas exitosas.
 * 
 * @par Ejemplo de uso:
 * @code
 * SensorManager sm;
 * sm.addSensor(new DhtSensor(22));
 * sm.begin(); // Inicializa buses (I2C, OneWire)
 * 
 * auto readings = sm.readAll();
 * for(auto& r : readings) {
 *     print(r.temperature);
 * }
 * @endcode
 */
class SensorManager {
private:
    std::vector<Demeter::ISensor*> _sensors; ///< Lista de sensores concretos registrados e incrustados.

public:
    /** @brief Constructor por defecto. */
    SensorManager();

    /**
     * @brief Añade una nueva entidad sensora a la pool manejada.
     * @param sensor Puntero polimórfico al sensor compatible con ISensor. 
     *               (Nota: el ciclo de vida actualmente lo transfiere lógicamente).
     */
    void addSensor(Demeter::ISensor* sensor);

    /**
     * @brief Inicializa todos los sensores registrados.
     * Itera sobre `_sensors` invocando `begin()` de forma concurrente,
     * garantizendo levantamiento de buses (como I2C o DallasTemperature).
     */
    void begin();

    /**
     * @brief Lee secuencialmente todos los sensores de la colección.
     * @return `std::vector<Demeter::SensorReading>` Lista limpia ignorando aquellos
     *         sensores que fallaron la lectura actual (isSuccess == false).
     */
    std::vector<Demeter::SensorReading> readAll();

    /**
     * @brief Devuelve la lista interna de punteros.
     * @return Referencia asíncrona a la configuración actual de hardware.
     */
    const std::vector<Demeter::ISensor*>& getSensors() const;
};
