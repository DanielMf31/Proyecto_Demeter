#pragma once

#include "communications/IComms.h"
#ifndef NATIVE_ENV
#include <esp_now.h>
#else
typedef int esp_now_send_status_t;
#endif
#include <map>
#include <array>
#include <vector>

/**
 * @class EspNowStrategy
 * @brief Implementación de IComms especializada en el stack ESP-NOW de Espressif.
 * 
 * Interfaz de radio 2.4GHz Point-to-Point transparente de baja latencia.
 * Gestiona automáticamente el registro de "Peers" dentro del subsistema de WiFi.
 * 
 * @par Ejemplo de uso:
 * @code
 * EspNowStrategy radio;
 * radio.begin();
 * 
 * // Registrar pasarela (normalmente desde un comando route_add)
 * std::array<uint8_t, 6> macGW = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
 * radio.registerRoute(1, macGW);
 * 
 * std::vector<uint8_t> payload = { 0xFE, 0... };
 * radio.send(payload.data(), payload.size());
 * @endcode
 */
class EspNowStrategy : public IComms {
public:
    EspNowStrategy();
    virtual ~EspNowStrategy();

    // IComms Interface
    /** @brief Inicializa WiFi en modo STA y arranca la capa ESP-NOW. */
    void begin() override;
    
    /** @brief Transmite trama asíncrona (usa esp_now_send). */
    void send(const uint8_t* data, size_t length) override;
    
    /** @brief Chequea si el callback RX llenó el buffer estático. */
    bool available() override;
    
    /** @brief Vacía y retorna el contenido encolado por el callback RX. */
    std::vector<uint8_t> read() override;
    
    /**
     * @brief Añade una entrada vinculante [ID -> MAC] en la tabla de ruteo.
     * Seguidamente llama a `esp_now_add_peer` en silicio.
     */
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override;

    // ESP-Now Callbacks (Static wrappers)
    static void onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status);
    static void onDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len);

#ifndef NATIVE_ENV
    // ESP32: Static members (Single Hardware Radio)
    static std::map<uint8_t, std::array<uint8_t, 6>> _routeTable;
    static std::vector<uint8_t> _rxBuffer;
    static bool _rxAvailable;
#else
    // NATIVE TEST: Instance members (Multiple Simulated Nodes)
    std::map<uint8_t, std::array<uint8_t, 6>> _routeTable;
    std::vector<uint8_t> _rxBuffer;
    bool _rxAvailable;
#endif
    
    /**
     * @brief Helper que inscribe un Peer al framework nativo.
     * @param mac Array de 6 bytes en bruto de la MAC detectada.
     */
    bool addPeer(const uint8_t* mac);
};
