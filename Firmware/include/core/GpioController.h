#pragma once

#include "core/InternalTypes.h"
#include "core/PinConfig.h"
#include <vector>

// Hardware Abstraction for GPIO
#include <Arduino.h>

/**
 * @class GpioController
 * @brief Capa de Abstracción de Hardware (HAL) para Control GPIO.
 * 
 * Gestiona los pines físicos del microcontrolador (ESP32).
 * Desacopla la lógica de negocio de la API de Arduino (digitalWrite, pinMode).
 * 
 * @par Ejemplo de uso:
 * @code
 * GpioController gpio;
 * gpio.setPins({4, 5});
 * gpio.init();
 * 
 * Demeter::SetGpioCmd cmd = {4, true, 0};
 * gpio.execute(cmd); // Pin 4 se pone a HIGH
 * @endcode
 */
class GpioController {
private:
    std::vector<uint8_t> _managedPins; ///< Vector con los pines inicializados por este controlador.

public:
    /**
     * @brief Configura la lista de pines gestionados.
     * @param pins Vector de números GPIO (Ej. {4, 5, 18}).
     */
    void setPins(const std::vector<uint8_t>& pins);

    /**
     * @brief Inicializa los pines GPIO configurados.
     * Recorre \p _managedPins, los configura como OUTPUT y los inicia a LOW por seguridad.
     */
    void init();

    /**
     * @brief Ejecuta una orden de Cómputo Digital sobre el Hardware.
     * 
     * Internamente invoca `digitalWrite` de la API de Arduino. Sólo actúa
     * sobre el pin si se encuentra dentro de `_managedPins` o si la orden 
     * tiene flags de "force".
     * 
     * @param cmd Estructura Demeter::SetGpioCmd con el target PIN y su nivel logico.
     */
    void execute(const Demeter::SetGpioCmd& cmd);
};
