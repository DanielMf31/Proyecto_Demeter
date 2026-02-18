#pragma once

#include "communications/IComms.h"
#include <vector>
#include <queue>
#include <map>
#include <memory>

/**
 * @brief Virtual Communication Strategy for Integration Testing.
 * Allows nodes to "send" data to a shared Virtual Bus, which then "delivers" it 
 * to other registered VirtualStrategy instances.
 */
class VirtualStrategy : public ICommunicationStrategy {
public:
    // Shared Bus (Static map of NodeID -> ReceiveQueue)
    // In a real implementation, this might be a singleton "VirtualEther".
    static std::map<uint8_t, std::queue<std::vector<uint8_t>>> _mailbox;
    static std::map<uint8_t, VirtualStrategy*> _instances;

    uint8_t _myNodeId;

    VirtualStrategy(uint8_t nodeId) : _myNodeId(nodeId) {
        _instances[nodeId] = this;
    }

    ~VirtualStrategy() {
        _instances.erase(_myNodeId);
    }

    void begin() override {
        // Clear my mailbox
        while(!_mailbox[_myNodeId].empty()) _mailbox[_myNodeId].pop();
    }

    void send(uint8_t targetNodeId, const uint8_t* data, size_t length) override {
        // "Broadcast" or Unicast Logic
        // If target is 0 (Broadcast), send to all OTHER instances
        // If target is specific, send only to that mailbox

        std::vector<uint8_t> packet(data, data + length);

        if (targetNodeId == 0) { // Broadcast
             for (auto& pair : _instances) {
                 if (pair.first != _myNodeId) {
                     _mailbox[pair.first].push(packet);
                 }
             }
        } else {
            // Unicast
            if (_instances.count(targetNodeId)) {
                _mailbox[targetNodeId].push(packet);
            }
        }
    }

    void update() override {
        // Nothing to do here, receive is polling-based via available()
    }

    bool available() override {
        return !_mailbox[_myNodeId].empty();
    }

    bool receive(uint8_t* senderId, uint8_t* data, size_t* length) override {
        if (_mailbox[_myNodeId].empty()) return false;

        std::vector<uint8_t> packet = _mailbox[_myNodeId].front();
        _mailbox[_myNodeId].pop();

        // Packet Structure from ProtocolEngine:
        // We need to extract SENDER ID for the interface.
        // Protocol Frame: [Sync][Len][Flags][Src][Dst]...
        // Src is at index 3.
        
        if (packet.size() > 3) {
            *senderId = packet[3];
        } else {
            *senderId = 0; // Error
        }

        if (data && length) {
            size_t copyLen = (*length < packet.size()) ? *length : packet.size();
            memcpy(data, packet.data(), copyLen);
            *length = copyLen;
        }

        return true;
    }

    // Helper for Test Setup
    static void resetBus() {
        _mailbox.clear();
        _instances.clear();
    }
};

// Define Static Members (Must be in a .cpp ideally, but for header-only mock/test simplicity):
// We'll put them in the test file or make this a .h/.cpp pair.
// For now, let's keep it header-only with inline? No, static members need definition.
// We will define them in the test file.
