#pragma once
#include <stdint.h>
#include "InternalTypes.h"
#include <vector>

namespace Demeter {

    /**
     * @class SystemContext
     * @brief Contexto Centralizado del Sistema Demeter.
     * 
     * Responsable de gestionar la identidad (Id, Rol), el estado 
     * actual de la conexión y la configuración de energía profunda 
     * (Deep Sleep) para el Nodo local.
     * 
     * @par Ejemplo de uso:
     * @code
     * SystemContext ctx;
     * ctx.setIdentity(2, NodeRole::SENSOR, 1);
     * ctx.setState(SystemState::RUNNING);
     * if (ctx.getState() == SystemState::RUNNING) {
     *     // Execute tasks
     * }
     * @endcode
     */
    class SystemContext {
    private:
        // --- Identity ---
        uint8_t _nodeId;       ///< ID lógico único de este nodo.
        uint8_t _gatewayId;    ///< ID de la pasarela destinada a procesar los envíos.
        NodeRole _role;        ///< ROL de este dispositivo en la red.
        
        // --- State ---
        SystemState _currentState; ///< Máquina de estado actual de la conexión/ejecución.
        uint16_t _batteryMv;       ///< Voltaje actual de la batería en mV.
        uint32_t _uptimeSeconds;   ///< Tiempo activo en segundos desde el arranque.
        uint8_t _lastErrorCode;    ///< Registro del último código de error.

        // --- Configuration ---
        bool _deepSleepEnabled;     ///< Flag global de gestión de ahorro de energía.
        uint32_t _reportIntervalMs; ///< Frecuencia objetivo para mandar reportes periódicos.
        std::vector<uint8_t> _activePins; ///< Pines IO que deben mantenerse tras el sleep.

    public:
        /**
         * @brief Constructor por defecto.
         */
        SystemContext();

        // Getters & Setters
        
        /**
         * @brief Define la identidad lógica y física de este nodo en la red.
         * 
         * @param id ID unívoca del nodo.
         * @param role Identificador del tipo de comportamiento (SENSOR, ACTUADOR, etc.).
         * @param gatewayId ID de la pasarela si estamos en modo nodo hoja.
         */
        void setIdentity(uint8_t id, NodeRole role, uint8_t gatewayId = 1);
        
        /** @return El ID numérico de este dispositivo. */
        uint8_t nodeId() const { return _nodeId; }
        
        /** @return El ID numérico de la Pasarela a la que enviar los datos. */
        uint8_t gatewayId() const { return _gatewayId; }
        
        /** @return El rol principal asinado (ej. NodeRole::SENSOR). */
        NodeRole role() const { return _role; }

        // State Management
        
        /**
         * @brief Actualiza la máquina de estado principal de la aplicación.
         * @param state El estado a establecer (por ej. SystemState::IDLE).
         */
        void setState(SystemState state);
        
        /** @return El estado actal del ciclo de vida del sistema. */
        SystemState getState() const { return _currentState; }
        
        /**
         * @brief Almacena la última medida del voltaje de alimentación.
         * @param mv Voltaje capturado en milivoltios.
         */
        void updateBattery(uint16_t mv);
        
        /** @return El último nivel de tensión sensado en mV. */
        uint16_t getBattery() const { return _batteryMv; }

        // Config
        
        /**
         * @brief Parametriza los reportes del ciclo principal de sistema.
         * 
         * @param intervalMs Tiempo de espera para recolectar datos a enviar en ms.
         * @param deepSleep true si debería dormirse entre un envío e intervalo de muestreo.
         */
        void setConfig(uint32_t intervalMs, bool deepSleep);
        
        /** @return true si deep sleep está activo, false en caso contrario. */
        bool isDeepSleepEnabled() const { return _deepSleepEnabled; }
        
        /** @return Ratio de frecuencia objetivo de envío de reportes (ms) */
        uint32_t getReportInterval() const { return _reportIntervalMs; }
    };
}
