#pragma once

#include <string>
#include <vector>
#include <cstdint>

/**
 * @file ISensor.h
 * @brief Interfaz para Sensores Modulares.
 */

namespace Demeter {

    /**
     * @brief Estructura Genérica para Lecturas de Sensores.
     * 
     * Soporta nativamente hasta dos magnitudes de punto flotante.
     * En Demeter V2, se utiliza predominantemente para Temp/Hum.
     * 
     * @par Ejemplo de uso:
     * @code
     * Demeter::SensorReading read = { 25.4f, 60.1f, true };
     * if (read.isValid) { sendTx(read); }
     * @endcode
     */
    struct SensorReading {
        float value1; ///< Valor de Medida 1 (ej. Temperatura en °C).
        float value2; ///< Valor de Medida 2 (ej. Humedad Relativa en %).
        bool isValid; ///< Flag de seguridad: true si el checksum/bus reportó éxito.
    };

    /**
     * @class ISensor
     * @brief Clase Base Abstracta (Interfaz) para todo hardware de sensado.
     * 
     * Garantiza un polimorfismo seguro. El SensorManager almacenará 
     * colecciones de `ISensor*` sin importarle si es I2C, UART, o Analógico.
     */
    class ISensor {
    public:
        virtual ~ISensor() = default;

        /**
         * @brief Inicializa el hardware del sensor.
         * Típicamente invoca a `.begin()` de la librería subyacente.
         * @return true si el sensor respondió correctamente al PING inicial.
         */
        virtual bool init() = 0;

        /**
         * @brief Ejecuta una lectura en caliente del bus de datos del sensor.
         * @param outReading Referencia a la estructura donde se inyectarán los datos lógicos.
         * @return true si la lectura eléctrica y lógica (CRC) fue exitosa.
         */
        virtual bool read(SensorReading& outReading) = 0;

        /**
         * @brief Obtiene el nombre del driver o sensor físico.
         * Utilidad para Logging o para mensajes de Debug por Serie.
         */
        virtual std::string getName() const = 0;
    };

}

