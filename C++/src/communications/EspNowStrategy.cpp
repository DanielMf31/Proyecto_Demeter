#include "communications/EspNowStrategy.h"
#include <Arduino.h>
#include <esp_now.h>
#include <esp_wifi.h>
#include <WiFi.h>
#include <cstring>

// Static members initialization
std::vector<uint8_t> EspNowStrategy::_rxBuffer;
std::map<uint8_t, std::array<uint8_t, 6>> EspNowStrategy::_routeTable;
bool EspNowStrategy::_rxAvailable = false;

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
    // ESP-Now requires sender and receiver on the same channel.
    // In STA mode, it might scan or default.
    // Force Channel 1.
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
    // Frame: SYNC(0) LEN(1) FLAGS(2) SRC(3) DST(4) CMD(5)
    uint8_t dstId = data[4];
    
    // Broadcast or Unicast?
    // If DST is 0xFF, broadcast? For now, we only support routed unicast.
    
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
        // Serial.printf("Unknown Route for ID: %d\n", dstId);
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
    // Serial.print("Last Packet Send Status: ");
    // Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void EspNowStrategy::onDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
    if (len < 6) return; // Ignore small packets
    
    // Auto-Learn Route
    // Frame: SYNC(0) LEN(1) FLAGS(2) SRC(3) DST(4) CMD(5)
    uint8_t srcId = incomingData[3];
    
    // Only learn valid IDs (1..254)
    if (srcId > 0 && srcId < 255) {
        std::array<uint8_t, 6> macArr;
        memcpy(macArr.data(), mac, 6);
        _routeTable[srcId] = macArr;
        
        // Also ensure peer exists (for sending back)
        // Note: For ESP-Now, we might need to add peer before sending.
        // We can't easily call addPeer (instance method) from here without instance.
        // But since we received from them, they are likely reachable? 
        // ESP-Now usually requires peer registration to SEND.
        // So we should try to add them if not exists.
        // For now, we just update the map. The send() function or registerRoute should handle addPeer.
        // Ideally we need to addPeer here. 
        
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
