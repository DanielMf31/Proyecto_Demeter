#pragma once

#include <stdint.h>
#include <stddef.h>
#include <vector>
#include <array>

/**
 * @class IComms
 * @brief Interfaz Abstracta para la Capa de Comunicaciones Físicas.
 * 
 * Implementa el Patrón Estrategia (Strategy Pattern) aislando el 
 * formato de los paquetes lógicos del medio físico subyacente.
 * Implementaciones concretas: UartStrategy, EspNowStrategy.
 * 
 * @par Ejemplo de uso polimórfico:
 * @code
 * IComms* comms = new EspNowStrategy();
 * comms->begin();
 * 
 * std::vector<uint8_t> payload = {0x01, 0xFF, 0x00};
 * comms->send(payload.data(), payload.size());
 * @endcode
 */
class IComms {
public:
    virtual ~IComms() {}

    /**
     * @brief Inicializa la interfaz hardware o protocolo de radio subyacente.
     * Ej. `Serial.begin(...)` para UART o `esp_now_init()` para ESP-NOW.
     */
    virtual void begin() = 0;

    /**
     * @brief Transmite un tren de bytes crudos a través del medio.
     * @param data Puntero al buffer constante de bytes a transmitir.
     * @param length Cantidad exacta de bytes del payload.
     */
    virtual void send(const uint8_t* data, size_t length) = 0;

    /**
     * @brief Comprueba subyacente si hay datos pendientes de consumir en el buffer RX.
     * @return true si al menos un byte se encuentra esperando en FIFO.
     */
    virtual bool available() = 0;

    /**
     * @brief Extrae todos los bytes disponibles del buffer RX del hardware.
     * 
     * @note Se devuelve por valor como `std::vector` asumiendo payloads 
     * pequeños (< 250 bytes en ESP-NOW y BLE) y confiando en Name/Return Value 
     * Optimization (RVO) del compilador C++14 para evitar la copia.
     * 
     * @return Vector continuo temporal con la trama extraída, en bruto.
     */
    virtual std::vector<uint8_t> read() = 0;

    /**
     * @brief Vincula lógicamente un Nodo Demeter a una dirección MAC física.
     * Únicamente utilizable en implementaciones multipunto inálambricas (ESP-NOW).
     * 
     * @param id ID lógico del nodo a enrutar (1 a 254).
     * @param mac Arreglo de 6 bytes correspondientes a la MAC del destinatario.
     * 
     * @note Implementación por defecto no hace nada, válido para P2P (UART).
     */
    virtual void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
        (void)id; (void)mac;
    }
};
