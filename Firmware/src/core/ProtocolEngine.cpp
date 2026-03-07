#include "core/ProtocolEngine.h"
#include <Arduino.h>
#include <cstring>
#include <vector>

/**
 * @file ProtocolEngine.cpp
 * @brief Protocolo Binario V2, empaquetado y decodificación.
 * 
 * ============================================================================
 * DECISIONES DE ARQUITECTURA Y DISEÑO
 * ============================================================================
 * 1. **Diseño "Zero Allocation" en la Recepción:** En sistemas embebidos
 *    evitamos hacer `new` u objetos String constantes. Parseamos los buffers
 *    planos usando Casteos C de alto rendimiento: `reinterpret_cast<Header*>`.
 * 2. **Desacoplamiento del Trasporte:** Este motor **no** abre puertos serie.
 *    Recibe una interfaz abstracta `IComms*` en su constructor y expulsa los
 *    tramas validados puros, ignorando si viajan por ESP-NOW, LoRa o UART.
 * 3. **Arquitectura basada en Eventos:** Internamente tiene punteros a funciones
 *    `std::function` (Callbacks). Cuando encuentra un comando válido, "avisa"
 *    a quien se haya suscrito (`_onGpioCommand`, `_onPingRecv`).
 */

// =============================================================
// SECTION: 1. Setup & Configuration (Parsing Logic)
// =============================================================

ProtocolEngine::ProtocolEngine(IComms* strategy) : _strategy(strategy) {}

void ProtocolEngine::setNodeId(uint8_t id) {
    _myId = id;
}

void ProtocolEngine::onSetGpio(Demeter::GpioCallback cb) {
    _onGpioCommand = cb;
}

void ProtocolEngine::onSetPwm(Demeter::PwmCallback cb) {
    _onPwmCommand = cb;
}

void ProtocolEngine::onExecSequence(Demeter::SequenceCallback cb) {
    _onSequenceCommand = cb;
}

void ProtocolEngine::onAckRecv(Demeter::AckCallback cb) { _onAckRecv = cb; }

void ProtocolEngine::onPingRecv(Demeter::PingCallback cb) {
    _onPingRecv = cb;
}

void ProtocolEngine::onTempHumReportRecv(Demeter::TempHumReportCallback cb) {
    _onTempHumReportRecv = cb;
}

void ProtocolEngine::onSensorClusterReportRecv(Demeter::SensorClusterReportCallback cb) {
    _onSensorClusterReport = cb;
}

void ProtocolEngine::onPinReportRecv(Demeter::PinReportCallback cb) { _onPinReport = cb; }
void ProtocolEngine::onSystemReportRecv(Demeter::SystemReportCallback cb) { _onSystemReport = cb; }
void ProtocolEngine::onGetSensorsRecv(Demeter::GetSensorsCallback cb) { _onGetSensors = cb; }
void ProtocolEngine::onRouteAddRecv(Demeter::RouteAddCallback cb) { _onRouteAdd = cb; }
void ProtocolEngine::onNackRecv(Demeter::NackCallback cb) { _onNack = cb; }
void ProtocolEngine::onSynRecv(Demeter::AckCallback cb) { _onSynRecv = cb; }
void ProtocolEngine::onSynAckRecv(Demeter::AckCallback cb) { _onSynAckRecv = cb; }

void ProtocolEngine::registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac) {
    if (_strategy) { // Changed from _commsStrategy to _strategy based on constructor
        _strategy->registerRoute(id, mac);
    }
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
 * @brief Logica nuclear de parseo de un frame que ingresa desde abajo (Capa de enlace).
 * 
 * ¿Por qué tantas validaciones rápidas antes del CRC?
 * Técnicas "Fail-Fast". Computar un CRC es computacionalmente costoso en un MCU
 * de baja potencia limitante a baterías.
 * Validamos mágicamente el Byte `sync` o el tamaño del paquete. Si fallan,
 * descartamos instantáneamente el array para ahorrar ciclos CPU y RAM.
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

    // 5. Forwarding Logic (Enrutamiento Nivel Red)
    // El Gateway (ID 1) tiene la directiva (FORCE-ACCEPT).
    // ¿Por qué? Un Gateway muchas veces debe "escuchar" paquetes destinados
    // al nodo servidor virtual (ID 0) para "hacerles puente" y sacarlos por la MAC puente.
    bool isForMe = (hdr->dst_id == _myId) || (hdr->dst_id == 0xFF);
    
    // Explicit Override: If I am the Gateway (ID 1) or if the message is for ID 1
    // and I'm configured to be the Gateway.
    if (_myId == 1 && hdr->dst_id == 1) {
        isForMe = true;
    }

    if (!isForMe) {
        // If destination is not ME, try to forward via Strategy.
        if (_strategy) {
            _strategy->send(frame.data(), frame.size());
        }
        return; // Don't execute locally
    }

    // 6. Command Dispatch
    Demeter::CommandType type = static_cast<Demeter::CommandType>(hdr->cmd_id);
    
    // Extracción de Payload para mayor limpieza conceptual.
    // Separamos la cabecera del cuerpo de datos, que según el tipo de comando
    // tendrá una forma distinta que será traducida por la máquina de estados.
    std::vector<uint8_t> payload;
    if (frame.size() > HEADER_SIZE + 1) {
        payload.assign(frame.begin() + HEADER_SIZE, frame.end() - 1);
    }

    // Switch gigantesco: El cerebro del parseo multiprotocolo.
    switch (type) {
        case Demeter::CommandType::PING: {
            // [Modified] No Auto-ACK. Delegated to SystemManager.
            if (_onPingRecv) {
                Demeter::RequestData req = {hdr->src_id};
                _onPingRecv(req);
            }
            break;
        }

        case Demeter::CommandType::ACK: {
            if (_onAckRecv && payload.size() >= 1) {
                Demeter::AckData ackData;
                ackData.sourceId = hdr->src_id;
                ackData.context = payload[0];
                _onAckRecv(ackData);
            }
            break;
        }

        case Demeter::CommandType::NACK: {
            if (_onNack && payload.size() >= 1) {
                Demeter::NackData nackData;
                nackData.sourceId = hdr->src_id;
                nackData.errorCode = payload[0];
                _onNack(nackData);
            }
            break;
        }

        case Demeter::CommandType::SYN: {
            if (_onSynRecv) {
                Demeter::AckData data = {hdr->src_id, 0};
                if (!payload.empty()) data.context = payload[0];
                _onSynRecv(data);
            }
            break;
        }

        case Demeter::CommandType::SYN_ACK: {
            if (_onSynAckRecv) {
                Demeter::AckData data = {hdr->src_id, 0};
                if (!payload.empty()) data.context = payload[0];
                _onSynAckRecv(data);
            }
            break;
        }

        case Demeter::CommandType::ROUTE_ADD: {
            // [Modified] No Auto-Registration or ACK. Delegated to SystemManager.
            // Payload: [TargetID(1)][MAC(6)]
            if (payload.size() >= 7 && _onRouteAdd) {
                Demeter::RouteAddCmd cmd;
                cmd.nodeId = payload[0];
                std::memcpy(cmd.mac.data(), &payload[1], 6);
                _onRouteAdd(cmd);
            }
            break;
        }

        case Demeter::CommandType::TEMP_HUM_REPORT: {
            if (payload.size() >= 4 && _onTempHumReportRecv) { // Fixed: Using _onTempHumReportRecv
                // Parse Payload: [T_L][T_H][H_L][H_H] (Int16 scaled x100)
                int16_t t_int = (int16_t)(payload[0] | (payload[1] << 8));
                int16_t h_int = (int16_t)(payload[2] | (payload[3] << 8));
                
                Demeter::TempHumReport report;
                report.sourceId = hdr->src_id;
                report.temperature = t_int / 100.0f;
                report.humidity = h_int / 100.0f;
                
                _onTempHumReportRecv(report);
            }
            break;
        }

        case Demeter::CommandType::SENSOR_CLUSTER_REPORT: {
            // Payload: [COUNT 1B] [ENTRY 6B] × N
            // Entry: [PLANT_ID_L][PLANT_ID_H][TEMP_L][TEMP_H][SOIL_L][SOIL_H]
            if (payload.size() >= 1 && _onSensorClusterReport) {
                uint8_t count = payload[0];
                size_t expected = 1 + (count * 6);
                if (payload.size() >= expected) {
                    Demeter::SensorClusterReport report;
                    report.sourceId = hdr->src_id;
                    size_t offset = 1;
                    for (uint8_t i = 0; i < count; i++) {
                        Demeter::SensorClusterEntry entry;
                        entry.plantId = (uint16_t)(payload[offset] | (payload[offset+1] << 8));
                        int16_t t_int = (int16_t)(payload[offset+2] | (payload[offset+3] << 8));
                        int16_t s_int = (int16_t)(payload[offset+4] | (payload[offset+5] << 8));
                        entry.temperature = t_int / 100.0f;
                        entry.soilMoisture = s_int / 100.0f;
                        report.entries.push_back(entry);
                        offset += 6;
                    }
                    _onSensorClusterReport(report);
                }
            }
            break;
        }

        case Demeter::CommandType::PIN_REPORT: {
            // Payload: [PIN][STATE]
            if (payload.size() >= 2 && _onPinReport) {
                Demeter::PinReport report;
                report.sourceId = hdr->src_id;
                report.pin = payload[0];
                report.state = (payload[1] != 0);
                _onPinReport(report);
            }
            break;
        }

        case Demeter::CommandType::SYSTEM_REPORT: {
             // Payload: [Mode][BattL][BattH]
             if (payload.size() >= 3 && _onSystemReport) {
                 Demeter::SystemReport report;
                 report.sourceId = hdr->src_id;
                 report.mode = payload[0];
                 report.batteryMv = (uint16_t)(payload[1] | (payload[2] << 8));
                 _onSystemReport(report);
             }
             break;
        }

        case Demeter::CommandType::GET_SENSORS: {
            if (_onGetSensors) {
                Demeter::RequestData req = {hdr->src_id};
                _onGetSensors(req);
            }
            break;
        }

        case Demeter::CommandType::SET_GPIO: {
            if (payload.size() >= 3 && _onGpioCommand) {
                Demeter::SetGpioCmd cmd;
                cmd.pin = payload[0];
                cmd.value = (payload[1] != 0);
                cmd.flags = payload[2];
                _onGpioCommand(cmd);
            }
            break;
        }

        case Demeter::CommandType::SET_PWM: {
            if (payload.size() >= 3 && _onPwmCommand) {
                Demeter::SetPwmCmd cmd;
                cmd.pin = payload[0];
                cmd.value = payload[1] | (payload[2] << 8);
                _onPwmCommand(cmd);
            }
            break;
        }

        case Demeter::CommandType::EXEC_SEQUENCE: {
             // Payload: [Count] [TGT][CMD][Pin][Val][DelayL][DelayH][DelayH][DelayH]... (8 bytes per step)
             if (payload.size() >= 1 && _onSequenceCommand) {
                 uint8_t count = payload[0];
                 size_t expected = 1 + (count * 8); 
                 if (payload.size() >= expected) {
                     Demeter::ExecSequenceCmd seqCmd;
                     size_t offset = 1;
                     for(int i=0; i<count; i++) {
                         Demeter::SequenceStep step;
                         // Skip Reserved TGT/CMD (2 bytes)
                         offset += 2;
                         step.pin = payload[offset++];
                         step.value = (payload[offset++] != 0);
                         uint32_t d = payload[offset++];
                         d |= (payload[offset++] << 8);
                         d |= (payload[offset++] << 16);
                         d |= (payload[offset++] << 24);
                         step.delayMs = d;
                         seqCmd.steps.push_back(step);
                     }
                     _onSequenceCommand(seqCmd);
                 }
             }
             break;
        }

        default:
            Serial.printf(">> [Engine] Unknown Command: 0x%02X\n", (uint8_t)type);
            break;
    }
}
   
// =============================================================
// SECTION: 2. High-Level Command Senders (Application Layer)
// =============================================================


// DATA REPORTS

void ProtocolEngine::sendTempHumReport(uint8_t targetId, const Demeter::TempHumReport& report) {
    std::vector<uint8_t> payload;
    payload.reserve(4);

    // Convert float to Int16 scaled x100
    // Example: 25.43 -> 2543
    int16_t t_int = (int16_t)(report.temperature * 100.0f);
    int16_t h_int = (int16_t)(report.humidity * 100.0f);

    // Serialize Little Endian
    payload.push_back((uint8_t)(t_int & 0xFF));
    payload.push_back((uint8_t)((t_int >> 8) & 0xFF));
    payload.push_back((uint8_t)(h_int & 0xFF));
    payload.push_back((uint8_t)((h_int >> 8) & 0xFF));

    sendFrame((uint8_t)Demeter::CommandType::TEMP_HUM_REPORT, targetId, payload);
}

void ProtocolEngine::sendSensorClusterReport(uint8_t targetId, const Demeter::SensorClusterReport& report) {
    std::vector<uint8_t> payload;
    payload.reserve(1 + report.entries.size() * 6);
    payload.push_back((uint8_t)report.entries.size());

    for (const auto& entry : report.entries) {
        // Plant ID (uint16 LE)
        payload.push_back((uint8_t)(entry.plantId & 0xFF));
        payload.push_back((uint8_t)((entry.plantId >> 8) & 0xFF));
        // Temperature (int16 LE, scaled x100)
        int16_t t_int = (int16_t)(entry.temperature * 100.0f);
        payload.push_back((uint8_t)(t_int & 0xFF));
        payload.push_back((uint8_t)((t_int >> 8) & 0xFF));
        // Soil moisture (int16 LE, scaled x100)
        int16_t s_int = (int16_t)(entry.soilMoisture * 100.0f);
        payload.push_back((uint8_t)(s_int & 0xFF));
        payload.push_back((uint8_t)((s_int >> 8) & 0xFF));
    }

    sendFrame((uint8_t)Demeter::CommandType::SENSOR_CLUSTER_REPORT, targetId, payload);
}

void ProtocolEngine::sendPinReport(uint8_t targetId, const Demeter::PinReport& report) {
    std::vector<uint8_t> payload;
    payload.reserve(2);
    payload.push_back(report.pin);
    payload.push_back(report.state ? 1 : 0);
    sendFrame((uint8_t)Demeter::CommandType::PIN_REPORT, targetId, payload);
}

void ProtocolEngine::sendSystemReport(uint8_t targetId, const Demeter::SystemReport& report) {
    std::vector<uint8_t> payload;
    payload.reserve(8);
    // [MODE(1)] [BATTERY(2)] [RESERVED(5)]
    payload.push_back(report.mode);
    payload.push_back((uint8_t)(report.batteryMv & 0xFF));
    payload.push_back((uint8_t)((report.batteryMv >> 8) & 0xFF));
    // Reserved padding
    for(int i=0; i<5; i++) payload.push_back(0x00);

    sendFrame((uint8_t)Demeter::CommandType::SYSTEM_REPORT, targetId, payload);
}

void ProtocolEngine::sendPing(uint8_t targetId, const Demeter::RequestData& data) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::PING, targetId, empty);
}

// HANDSHAKE


void ProtocolEngine::sendSyn(uint8_t targetId, const Demeter::AckData& data) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::SYN, targetId, empty);
}

void ProtocolEngine::sendSynAck(uint8_t targetId, const Demeter::AckData& data) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::SYN_ACK, targetId, empty);
}

void ProtocolEngine::sendAck(uint8_t targetId, const Demeter::AckData& data) {
    std::vector<uint8_t> payload;
    if (data.context != 0) {
        payload.push_back(data.context);
    }
    sendFrame((uint8_t)Demeter::CommandType::ACK, targetId, payload);
}

void ProtocolEngine::sendNack(uint8_t targetId) {
    std::vector<uint8_t> payload;
    payload.push_back(0xFF); // Default Generic Error
    sendFrame((uint8_t)Demeter::CommandType::NACK, targetId, payload);
}



// ACTION REQUESTS

void ProtocolEngine::sendSetGpio(uint8_t targetId, const Demeter::SetGpioCmd& cmd) {
    std::vector<uint8_t> payload;
    payload.reserve(3);
    payload.push_back(cmd.pin);
    payload.push_back(cmd.value ? 1 : 0);
    payload.push_back(cmd.flags); // Flags
    sendFrame((uint8_t)Demeter::CommandType::SET_GPIO, targetId, payload);
}

void ProtocolEngine::sendGetSensors(uint8_t targetId, const Demeter::RequestData& data) {
    std::vector<uint8_t> empty;
    sendFrame((uint8_t)Demeter::CommandType::GET_SENSORS, targetId, empty);
}

void ProtocolEngine::sendExecSequence(uint8_t targetId, const Demeter::ExecSequenceCmd& cmd) {
    std::vector<uint8_t> payload;
    // Format: [Count] [Step1...] [Step2...]
    // Step: [TGT=0][CMD=0][PIN][VAL][DELAY(4)]
    
    payload.reserve(1 + cmd.steps.size() * 8);
    payload.push_back((uint8_t)cmd.steps.size());
    
    for(const auto& step : cmd.steps) {
        payload.push_back(0); // TGT (future use)
        payload.push_back(0); // CMD (future use)
        payload.push_back(step.pin);
        payload.push_back(step.value ? 1 : 0);
        
        // Delay 32-bit Little Endian
        payload.push_back((uint8_t)(step.delayMs & 0xFF));
        payload.push_back((uint8_t)((step.delayMs >> 8) & 0xFF));
        payload.push_back((uint8_t)((step.delayMs >> 16) & 0xFF));
        payload.push_back((uint8_t)((step.delayMs >> 24) & 0xFF));
    }

    sendFrame((uint8_t)Demeter::CommandType::EXEC_SEQUENCE, targetId, payload);
}

// =============================================================
// SECTION: 3. Low-Level Send Logic (Transport Layer)
// =============================================================

/**
 * @brief Función interna "constructora" (Builder) del motor emisor.
 * 
 * Empaqueta un array plano con los datos de un comando sumándole 
 * un Header robusto por delante y el Checker Algorítmico al final (CRC).
 * ¿Por qué separarlo? Permite centralizar la suma de comprobación (CRC)
 * independientemente del payload sin repetirlo por cada rutina.
 */
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
