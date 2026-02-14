#include "communications/EspNowStrategy.h"
#include <Arduino.h>
#include <cstring>
#include <vector>

#ifndef NATIVE_ENV
#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>
#endif

#ifndef NATIVE_ENV
// Static members initialization (Real Hardware Only)
std::vector<uint8_t> EspNowStrategy::_rxBuffer;
std::map<uint8_t, std::array<uint8_t, 6>> EspNowStrategy::_routeTable;
bool EspNowStrategy::_rxAvailable = false;
#endif

#ifdef NATIVE_ENV
// -----------------------------------------------------------------------------
// NATIVE TEST SIMULATION (Multi-Node)
// -----------------------------------------------------------------------------

// Registry of all active "Nodes" (Strategies)
static std::vector<EspNowStrategy*> _instances;

EspNowStrategy::EspNowStrategy() {
    _instances.push_back(this);
}

EspNowStrategy::~EspNowStrategy() {
    // Remove self from registry
    auto it = std::find(_instances.begin(), _instances.end(), this);
    if (it != _instances.end()) {
        _instances.erase(it);
    }
}

void EspNowStrategy::begin() {
    // No hardware init needed
}

void EspNowStrategy::registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
    _routeTable[id] = mac;
}

bool EspNowStrategy::addPeer(const uint8_t* mac) { return true; }

void EspNowStrategy::send(const uint8_t* data, size_t length) {
    if (length < 6) return;

    // Simulate Broadcast/Multicast in the "Ether"
    // We send to ALL other instances. They will filter by MAC/ID if they implemented full filtering.
    // For simplicity here, we push to everyone else's buffer.
    
    for (auto* node : _instances) {
        if (node == this) continue; // Don't hear yourself

        // Direct Injection to Neighbor's RX Buffer
        // In real ESP-Now, you get (mac, data, len).
        // We simulate the `onDataRecv` behavior by pushing to their buffer.
        
        node->_rxBuffer.assign(data, data + length);
        node->_rxAvailable = true;
    }
}

bool EspNowStrategy::available() { return _rxAvailable; }

std::vector<uint8_t> EspNowStrategy::read() {
    if (_rxAvailable) {
        _rxAvailable = false;
        return _rxBuffer;
    }
    return {};
}

// Static callbacks unused in native test, but kept for compilation if referenced
void EspNowStrategy::onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {}
void EspNowStrategy::onDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {}

#else

// Real Implementation
EspNowStrategy::EspNowStrategy() {
    _rxBuffer.reserve(250);
}

EspNowStrategy::~EspNowStrategy() {}

void EspNowStrategy::begin() {
    // Init WiFi in Station Mode
    WiFi.mode(WIFI_STA);
    
    if (esp_now_init() != ESP_OK) {
        Serial.println("Error initializing ESP-NOW");
        return;
    }
    
    // START FIX: ESP32-S3 Channel Mismatch Fix
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
    esp_wifi_set_promiscuous(false);
    Serial.println("ESP-Now Channel set to 1");
    // END FIX

    // Register Callbacks
    esp_now_register_send_cb(EspNowStrategy::onDataSent);
    esp_now_register_recv_cb(EspNowStrategy::onDataRecv);
    
    Serial.println("ESP-NOW Initialized");
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
}

void EspNowStrategy::registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
    _routeTable[id] = mac;
    
    // Also register as peer in ESP-Now
    addPeer(mac.data());
}

bool EspNowStrategy::addPeer(const uint8_t* mac) {
    esp_now_peer_info_t peerInfo = {}; // Zero-initialize
    memcpy(peerInfo.peer_addr, mac, 6);
    peerInfo.channel = 0;  
    peerInfo.encrypt = false;
    
    if (esp_now_add_peer(&peerInfo) != ESP_OK){
        if (esp_now_is_peer_exist(mac)) {
            Serial.println("DEBUG: Peer already exists.");
            return true;
        }
        Serial.println("ERROR: Failed to add peer!");
        return false;
    }
    Serial.printf("DEBUG: Peer added: %02X:%02X:%02X:%02X:%02X:%02X\n", 
                  mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
    return true;
}

void EspNowStrategy::send(const uint8_t* data, size_t length) {
    if (length < 6) return; // Min header
    
    // Extract Dest ID from Frame (Index 4)
    uint8_t dstId = data[4];
    
    // Find MAC
    auto it = _routeTable.find(dstId);
    if (it != _routeTable.end()) {
        const uint8_t* targetMac = it->second.data();
        esp_err_t result = esp_now_send(targetMac, data, length);
        
        if (result != ESP_OK) {
            Serial.printf("ERROR: ESP-Now Send Failed: %s\n", esp_err_to_name(result));
        } else {
            Serial.printf("DEBUG: ESP-Now Send OK to ID %d\n", dstId);
        }
    } else {
        // Unknown Route
    }
}

bool EspNowStrategy::available() {
    return _rxAvailable;
}

std::vector<uint8_t> EspNowStrategy::read() {
    if (_rxAvailable) {
        _rxAvailable = false;
        return _rxBuffer; // Return copy
    }
    return {};
}

// Callbacks
void EspNowStrategy::onDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
    // Optional: Update status or log
}

void EspNowStrategy::onDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
    if (len < 6) return; // Ignore small packets
    
    // Auto-Learn Route
    uint8_t srcId = incomingData[3];
    uint8_t dstId = incomingData[4];
    uint8_t cmdId = incomingData[5];

    Serial.printf(">> [ESP-NOW] RX: %d bytes from %02X:%02X:%02X:%02X:%02X:%02X | Src:%d Dst:%d Cmd:%d\n", 
                  len, mac[0], mac[1], mac[2], mac[3], mac[4], mac[5], srcId, dstId, cmdId);
    
    // Only learn valid IDs (1..254)
    if (srcId > 0 && srcId < 255) {
        std::array<uint8_t, 6> macArr;
        memcpy(macArr.data(), mac, 6);
        _routeTable[srcId] = macArr;
        
        esp_now_peer_info_t peerInfo = {};
        memcpy(peerInfo.peer_addr, mac, 6);
        peerInfo.channel = 0;
        peerInfo.encrypt = false;
        
        if (!esp_now_is_peer_exist(mac)) {
            esp_now_add_peer(&peerInfo);
        }
    }

    _rxBuffer.assign(incomingData, incomingData + len);
    _rxAvailable = true;
}
#endif
