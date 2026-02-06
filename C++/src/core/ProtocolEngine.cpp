#include "core/ProtocolEngine.h"
#include <cstring>
#include <vector>

ProtocolEngine::ProtocolEngine(IComms* strategy) : _strategy(strategy) {}

void ProtocolEngine::onSetGpio(GpioCallback cb) {
    _onGpioCommand = cb;
}

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
    // Frame: [SYNC][LEN][FLAGS][SRC][DST][CMD] ... [PAYLOAD] ... [CRC]
    // Index:   0     1     2      3    4    5        6...          END
    
    const uint8_t* dataStart = frame.data() + 1; // Skip Sync
    size_t dataLen = (HEADER_SIZE - 1) + hdr->length;
    
    uint8_t calcCRC = calculateCRC(dataStart, dataLen);
    uint8_t recvCRC = frame[HEADER_SIZE + hdr->length];

    if (calcCRC != recvCRC) {
        // CRC Error
        return;
    }

    // 5. Dispatch based on CMD
    if (hdr->cmd_id == (uint8_t)Demeter::CommandType::SET_GPIO) {
        if (hdr->length >= 3 && _onGpioCommand) {
            Demeter::SetGpioCmd cmd;
            const uint8_t* payloadPtr = frame.data() + HEADER_SIZE;
            
            cmd.pin = payloadPtr[0];
            cmd.value = (payloadPtr[1] > 0);
            cmd.flags = payloadPtr[2];
            
            _onGpioCommand(cmd);
        }
    }
}
