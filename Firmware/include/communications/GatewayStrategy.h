#pragma once

#include "communications/IComms.h"
#include <vector>

/**
 * @class GatewayStrategy
 * @brief Estrategia Combinada (Composite Pattern) diseñada para Pasarelas.
 * 
 * Actúa como puente bidireccional entre la Subred en el Borde (ej. ESP-NOW) 
 * y la Red Backhaul (ej. UART hacia Raspberry Pi). Enruta el tráfico leyendo
 * cabeceras al vuelo hacia la interfaz que corresponda.
 * 
 * @par Ejemplo de uso:
 * @code
 * UartStrategy uart(&Serial, 115200);
 * EspNowStrategy radio;
 * GatewayStrategy gwComms(&uart, &radio);
 * 
 * gwComms.begin(); // Inicializa ambas debajo.
 * ProtocolEngine engine(&gwComms);
 * @endcode
 */
class GatewayStrategy : public IComms {
public:
    /**
     * @brief Inyecta las interfazes físicas subyacentes.
     * @param uart Estrategia serie, comunicada localmente con Servidor IT.
     * @param espNow Estrategia OTA conectada en malla estrella con Invernadero.
     */
    GatewayStrategy(IComms* uart, IComms* espNow);

    /** @brief Detona el arranque sucesivo de `uart->begin()` y `espNow->begin()`. */
    void begin() override;
    
    /** @brief Delega la inscripción de MACS a la estrategia ESP-NOW inyectada. */
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) override;
    
    /** @brief Broadcast! Emite la misma trama en serie y por radio simultáneamente. */
    void send(const uint8_t* data, size_t length) override;
    
    /** @brief Or lógico entre `uart->available()` || `espNow->available()`. */
    bool available() override;
    
    /**
     * @brief Vacía el buffer de la primera interfaz que reporte datos (Prioridad: UART).
     * @note El Engine procesa tramas unitarias; si ambas tienen, iterará en el sgte tick.
     */
    std::vector<uint8_t> read() override;

private:
    IComms* _uart;
    IComms* _espNow;
};
