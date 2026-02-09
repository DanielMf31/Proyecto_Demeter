#include "core/ProtocolEngine.h"
#include <Arduino.h>
#include <cstring>
#include <vector>

/**
 * @file ProtocolEngine.cpp
 * @brief Logic for Frame Parsing and Validation.
 */

ProtocolEngine::ProtocolEngine(IComms* strategy) : _strategy(strategy) {}

void ProtocolEngine::onSetGpio(GpioCallback cb) {
    _onGpioCommand = cb;
}

void ProtocolEngine::onSetPwm(PwmCallback cb) {
    _onPwmCommand = cb;
}

void ProtocolEngine::onExecSequence(SequenceCallback cb) {
    _onSequenceCommand = cb;
}

void ProtocolEngine::onAckRecv(AckCallback cb) {
    _onAckRecv = cb;
}

void ProtocolEngine::onPingRecv(PingCallback cb) {
    _onPingRecv = cb;
}

void ProtocolEngine::onDataReportRecv(DataReportCallback cb) {
    _onDataReportRecv = cb;
}

/**
 * @brief Calculates a simple Modular Sum CRC (Mod 256).
 * @param data Pointer to data buffer.
 * @param len Length of data in bytes.
 * @return uint8_t Calculated CRC.
 */
uint8_t ProtocolEngine::calculateCRC(const uint8_t* data, size_t len) {
    uint32_t sum = 0;
    for (size_t i = 0; i < len; i++) {
        sum += data[i];
    }
    return (uint8_t)(sum % 256);
}

void ProtocolEngine::update() {
    if (_strategy && _strategy->available()) {
        std::vector<uint8_t> buffer = _strategy->read();
        if (!buffer.empty()) {
            parseFrame(buffer);
        }
    }
}

/**
 * @brief Core parsing logic for a received frame.
 * Validates Header, Sync, Length and CRC before dispatching.
 */
void ProtocolEngine::parseFrame(const std::vector<uint8_t>& frame) {
    if (frame.size() < HEADER_SIZE + 1) return; // Min: Header + CRC

    // 1. Cast Header
    const Header* hdr = reinterpret_cast<const Header*>(frame.data());

    // 2. Sync Check
    if (hdr->sync != SYNC_BYTE) return;

    // 3. Length Check
    size_t expectedLen = HEADER_SIZE + hdr->length + 1;
    if (frame.size() < expectedLen) return;

    // 4. CRC Validation
    // CRC is over Header[1:] + Payload
    const uint8_t* dataStart = frame.data() + 1; // Skip Sync
    size_t dataLen = (HEADER_SIZE - 1) + hdr->length;
    
    uint8_t calcCRC = calculateCRC(dataStart, dataLen);
    uint8_t recvCRC = frame[HEADER_SIZE + hdr->length];

    if (calcCRC != recvCRC) {
        // CRC Error
        return;
    }

    // 5. Forwarding Logic
    // If destination is not ME, try to forward via Strategy.
    if (hdr->dst_id != _myId && hdr->dst_id != 0xFF) { // Assuming 0xFF is Broadcast? Or check if not Broadcast.
        // Note: We might want to execute Broadcasts AND forward them? 
        // For now, simple unicast forwarding.
        if (_strategy) {
            _strategy->send(frame.data(), frame.size());
        }
        return; // Don't execute locally
    }

    // 6. Dispatch based on CMD
    if (hdr->cmd_id == 0x0A) { // ROUTE_ADD
        Serial.println(">> RX: ROUTE_ADD Command");
        if (hdr->length >= 7) { // 1 byte ID + 6 bytes MAC
            const uint8_t* payloadPtr = frame.data() + HEADER_SIZE;
            uint8_t nodeId = payloadPtr[0];
            std::array<uint8_t, 6> mac;
            std::copy(payloadPtr + 1, payloadPtr + 7, mac.begin());
            
            if (_strategy) {
                _strategy->registerRoute(nodeId, mac);
            }
            sendAck(hdr->src_id);
        } else {
            sendNack(hdr->src_id);
        }
        return;
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::SET_GPIO) {
        if (hdr->length >= 3 && _onGpioCommand) {
            Demeter::SetGpioCmd cmd;
            const uint8_t* payloadPtr = frame.data() + HEADER_SIZE;
            
            cmd.pin = payloadPtr[0];
            cmd.value = (payloadPtr[1] > 0);
            cmd.flags = payloadPtr[2];
            
            _onGpioCommand(cmd);
        }
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::SET_PWM) {
        if (hdr->length >= 3 && _onPwmCommand) {
            Demeter::SetPwmCmd cmd;
            const uint8_t* payloadPtr = frame.data() + HEADER_SIZE;

            cmd.pin = payloadPtr[0];
            // Little Endian: Low Byte First
            cmd.value = payloadPtr[1] | (payloadPtr[2] << 8);

            _onPwmCommand(cmd);
        }
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::EXEC_SEQUENCE) {
        if (hdr->length >= 1 && _onSequenceCommand) {
            Demeter::ExecSequenceCmd cmd;
            const uint8_t* payloadPtr = frame.data() + HEADER_SIZE;
            
            uint8_t count = payloadPtr[0];
            size_t offset = 1;
            
            for (uint8_t i = 0; i < count; i++) {
                // Ensure we don't read past the frame
                if (offset + 8 > hdr->length) break;
                
                Demeter::SequenceStep step;
                // Format: [TGT] [CMD] [PIN] [VAL] [DELAY(4)]
                
                // step.target = payloadPtr[offset + 0]; // Ignored for now
                // step.cmd    = payloadPtr[offset + 1]; // Ignored for now
                step.pin = payloadPtr[offset + 2];
                step.value = (payloadPtr[offset + 3] > 0);
                
                // Extract 32-bit Delay (Little Endian)
                uint32_t delay = payloadPtr[offset + 4] | 
                                 (payloadPtr[offset + 5] << 8) |
                                 (payloadPtr[offset + 6] << 16) |
                                 (payloadPtr[offset + 7] << 24);
                step.delayMs = delay;
                
                cmd.steps.push_back(step);
                offset += 8;
            }
            
            _onSequenceCommand(cmd);
        }
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::PING) {
        if (_onPingRecv) {
            _onPingRecv(hdr->src_id);
        }
        // Respond with ACK
        sendAck(hdr->src_id);
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::ACK) {
        if (_onAckRecv) {
            _onAckRecv(hdr->src_id);
        }
    }
    else if (hdr->cmd_id == (uint8_t)Demeter::CommandType::DATA_REPORT) {
        if (hdr->length >= 4 && _onDataReportRecv) {
            // Payload: [TempLSB] [TempMSB] [HumLSB] [HumMSB]
            const uint8_t* p = frame.data() + HEADER_SIZE;
            int16_t t_int = p[0] | (p[1] << 8);
            int16_t h_int = p[2] | (p[3] << 8);
            
            float temp = t_int / 100.0f;
            float hum = h_int / 100.0f;
            
            _onDataReportRecv(hdr->src_id, temp, hum);
        }
        // Also send ACK? Usually telemetry is fire-and-forget or ACKed.
        // Let's ACK for reliability if needed, but might congest.
        // User didn't specify. Let's NOT Ack for now to save bandwidth.
    }
}

void ProtocolEngine::sendAck(uint8_t targetId) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::ACK, targetId, empty);
}

void ProtocolEngine::sendPing(uint8_t targetId) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::PING, targetId, empty);
}

void ProtocolEngine::sendDataReport(uint8_t targetId, float temp, float hum) {
    std::vector<uint8_t> payload;
    payload.reserve(4);

    // Convert float to Int16 scaled x100
    // Example: 25.43 -> 2543
    int16_t t_int = (int16_t)(temp * 100.0f);
    int16_t h_int = (int16_t)(hum * 100.0f);

    // Serialize Little Endian
    payload.push_back((uint8_t)(t_int & 0xFF));
    payload.push_back((uint8_t)((t_int >> 8) & 0xFF));
    payload.push_back((uint8_t)(h_int & 0xFF));
    payload.push_back((uint8_t)((h_int >> 8) & 0xFF));

    sendFrame((uint8_t)Demeter::CommandType::DATA_REPORT, targetId, payload);
}

void ProtocolEngine::sendNack(uint8_t targetId) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::NACK, targetId, empty);
}

void ProtocolEngine::setNodeId(uint8_t id) {
    _myId = id;
}

void ProtocolEngine::sendFrame(uint8_t cmdId, uint8_t targetId, const std::vector<uint8_t>& payload) {
    if (!_strategy) return;

    std::vector<uint8_t> frame;
    frame.reserve(HEADER_SIZE + payload.size() + 1);

    // Header
    Header hdr;
    hdr.sync = SYNC_BYTE;
    hdr.length = (uint8_t)payload.size();
    hdr.flags = 0x00;
    hdr.src_id = _myId;
    hdr.dst_id = targetId;
    hdr.cmd_id = cmdId;
    
    // Serialize Header
    const uint8_t* hdrPtr = reinterpret_cast<const uint8_t*>(&hdr);
    frame.insert(frame.end(), hdrPtr, hdrPtr + HEADER_SIZE);

    // Payload
    frame.insert(frame.end(), payload.begin(), payload.end());

    // CRC
    const uint8_t* dataStart = frame.data() + 1; // Skip Sync
    size_t dataLen = (HEADER_SIZE - 1) + payload.size();
    uint8_t crc = calculateCRC(dataStart, dataLen);
    
    frame.push_back(crc);

    _strategy->send(frame.data(), frame.size());
}
