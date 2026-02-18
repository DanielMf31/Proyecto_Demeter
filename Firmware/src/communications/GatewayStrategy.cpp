#include "communications/GatewayStrategy.h"

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

void GatewayStrategy::send(const uint8_t* data, size_t length) {
    if (length < 6) return;

    // Extract Destination ID (Index 4 in Protocol V2 Frame)
    // [SYNC] [LEN] [FLAGS] [SRC] [DST]
    uint8_t dstId = data[4];

    if (dstId == 0) {
        // ID 0 is reserved for Host -> Send via UART
        if (_uart) _uart->send(data, length);
    } else {
        // All other valid IDs are presumably Nodes -> Send via ESP-Now
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
