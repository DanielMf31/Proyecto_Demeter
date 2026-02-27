#include "core/GpioController.h"

/**
 * @file GpioController.cpp
 * @brief Implementación de la Abstracción de Hardware GPIO.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Defensa en Profundidad (Defense in Depth):** ¿Por qué no usamos
 *    `digitalWrite()` libremente a lo largo del código?
 *    Delegar el hardware a esta clase permite añadir escudos protectores.
 *    La lista `_managedPins` actúa como una "Lista Blanca". Si por un fallo de
 *    red o hackeo llega un comando pidiendo encender el Pin 1 (UART TX),
 *    este controlador lo rechazará silenciosamente, evitando colapsar el micro.
 */

/**
 * @brief Registra qué pines están permitidos para este nodo.
 * 
 * Se llama desde el archivo `main_*.cpp` o la inicialización del Nodo.
 * Filtra automáticamente pines prohibidos usando la protección estática de BSP.
 */
void GpioController::setPins(const std::vector<uint8_t>& pins) {
    _managedPins.clear();
    for(uint8_t pin : pins) {
        // Enforce BSP Protection (Board Support Package)
        if(isPinProtected(pin)) {
            // Rechazo silencioso para no romper flujos masivos.
            continue;
        }
        _managedPins.push_back(pin);
    }
}

void GpioController::init() {
    if (_managedPins.empty()) {
        return;
    }

    for (uint8_t pin : _managedPins) {
        // Double check just in case, though setPins handles it.
        if(!isPinProtected(pin)) {
             pinMode(pin, OUTPUT);
             digitalWrite(pin, LOW); // Start OFF
        }
    }
}

/**
 * @brief Recibe un objeto comando estructurado y lo inyecta al hardware.
 * 
 * ¿Por qué el argumento es `Demeter::SetGpioCmd` y no `(uint8_t pin, bool val)`?
 * Facilita extender el protocolo. Si mañana el comando añade parámetros como
 * `duration` o `fade_speed` (para PWM), la firma de esta función no se rompe,
 * solo se extrae el nuevo campo del Struct.
 */
void GpioController::execute(const Demeter::SetGpioCmd& cmd) {
    // 1. Validation: ¿Nos petenece este pin? Lista Blanca.
    bool isManaged = false;
    for (uint8_t pin : _managedPins) {
        if (pin == cmd.pin) {
            isManaged = true;
            break;
        }
    }

    if (!isManaged) return; // Silent Fail: We don't control this pin.

    // 2. Redudant Safety Check
    // "Trust no one". Volvemos a chequear por si la lista fue corrompida en memoria.
    if(isPinProtected(cmd.pin)) return;

    // 3. Actuate
    digitalWrite(cmd.pin, cmd.value ? HIGH : LOW);
}
