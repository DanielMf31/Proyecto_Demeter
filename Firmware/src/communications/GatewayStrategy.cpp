#include "communications/GatewayStrategy.h"

/**
 * @file GatewayStrategy.cpp
 * @brief Implementación del enrutador híbrido (Multiplexor).
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Patrón Decorador / Proxy:** Al sistema central no le importa que el Gateway
 *    tenga dos tarjetas de red (Puerto Serie y Antena WiFi). El `GatewayStrategy`
 *    implementa `IComms` (es una estrategia), pero recibe dos `IComms` en su constructor.
 *    Básicamente intercepta los `.send()` y decide a quién "sub-enrutarlo".
 * 2. **Enrutamiento por ID (ID 0):** En Demeter, el ID 0 está reservado para el
 *    "Servidor Host" (backend en Raspberry Pi). Si el frame detecta Destino=0, sale
 *    por el cable USB/UART. Cualquier otro ID viaja por WiFi P2P (ESP-NOW) hacia
 *    los nodos de la finca.
 */

// Constructor
GatewayStrategy::GatewayStrategy(IComms* uart, IComms* espNow) 
    : _uart(uart), _espNow(espNow) {}

void GatewayStrategy::begin() {
    if (_uart) _uart->begin();
    if (_espNow) _espNow->begin();
}

void GatewayStrategy::registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
    // Routes are typically for the wireless network (ESP-Now)
    if (_espNow) _espNow->registerRoute(id, mac);
}

/**
 * @brief Funcionalidad core de capa de red (Muxer).
 * Intercepta los bytes salientes, lee el ID destino nativo del protocolo
 * y lo bifurca a un cable serie o al aire libre según la topología lógica.
 */
void GatewayStrategy::send(const uint8_t* data, size_t length) {
    if (length < 6) return;

    // Extract Destination ID (Index 4 in Protocol V2 Frame)
    // [SYNC] [LEN] [FLAGS] [SRC] [DST]
    uint8_t dstId = data[4];

    if (dstId == 0) {
        // ID 0 is reserved for Host -> Send via local hardwired UART (Pi)
        if (_uart) _uart->send(data, length);
    } else {
        // All other valid IDs are presumably Nodes -> Send via ESP-Now Mesh
        if (_espNow) _espNow->send(data, length);
    }
}

bool GatewayStrategy::available() {
    bool u = _uart ? _uart->available() : false;
    bool e = _espNow ? _espNow->available() : false;
    return u || e;
}

std::vector<uint8_t> GatewayStrategy::read() {
    // Priority: Host (UART) Commands > Node (ESP-Now) Responses
    if (_uart && _uart->available()) {
        return _uart->read();
    }
    if (_espNow && _espNow->available()) {
        return _espNow->read();
    }
    return {};
}
