#pragma once

#include <array>
#include "communications/IComms.h"
#include "core/InternalTypes.h"
#include <functional>
#include <vector>
#include <cstdint>
#include <cstddef>

/**
 * @class ProtocolEngine
 * @brief Motor Central de Procesamiento del Protocolo Binario (V2).
 * 
 * Se encarga de la Codificación/Decodificación (Serialization), 
 * Validación de Integridad (CRC) y Enrutamiento Funcional (Callbacks).
 * Transforma un tren de bytes entrante en estructuras lógicas Demeter.
 * 
 * @par Ejemplo de uso:
 * @code
 * IComms* uart = new UartStrategy();
 * ProtocolEngine engine(uart);
 * engine.setNodeId(DEVICE_ID);
 * 
 * engine.onSetGpio([](const Demeter::SetGpioCmd& cmd) {
 *     // Actuar sobre el pin
 * });
 * 
 * void loop() {
 *     engine.update(); // Mantiene procesando la cola RX
 * }
 * @endcode
 */
class ProtocolEngine {
public:
    // Protocol Constants
    static const uint8_t SYNC_BYTE = 0xFE;

    /**
     * @brief Estructura Empaquetada de la Cabecera (Header) del Protocolo.
     * Garantiza un alineamiento a nivel de byte en memoria para una 
     * serialización/deserialización directa sobre el buffer (Zero-copy approach).
     */
    struct Header {
        uint8_t sync;       ///< Byte de Sincronismo Fijo (0xFE).
        uint8_t length;     ///< Longitud exacta del Payload (sin Header ni CRC).
        uint8_t flags;      ///< Máscara de bits para metadatos (ej. requiere ACK).
        uint8_t src_id;     ///< ID Lógico del Nodo Emisor.
        uint8_t dst_id;     ///< ID Lógico del Nodo Destinatario (0 = Broadcast).
        uint8_t cmd_id;     ///< Identificador del Comando (CommandType).
    } __attribute__((packed));

    static const size_t HEADER_SIZE = sizeof(Header);

    // =============================================================
    // SECTION: 1. Setup & Configuration (Parsing Logic)
    // =============================================================
    ProtocolEngine(IComms* strategy);

    /**
     * @brief Asigna el ID Lógico originador incrustado en los Headers salientes.
     * @param id ID único de 1 a 254.
     */
    void setNodeId(uint8_t id);

    /**
     * @brief Bucle Principal del Parsing (Fase Lógica).
     * 
     * Extrae de la interfaz `IComms` un tren de bytes, extrae cabecera, 
     * valida CRC, deserializa el payload CBOR y desencadena el Callback 
     * correspondiente según el `cmd_id` registrado.
     * 
     * @note Se debe llamar asiduamente para no rebalsar los buffers RX.
     */
    void update();

    // Callback Setters
    void onSetGpio(Demeter::GpioCallback cb);
    void onSetPwm(Demeter::PwmCallback cb);
    void onExecSequence(Demeter::SequenceCallback cb);
    void onAckRecv(Demeter::AckCallback cb);
    void onPingRecv(Demeter::PingCallback cb);
    void onTempHumReportRecv(Demeter::TempHumReportCallback cb);
    void onSensorClusterReportRecv(Demeter::SensorClusterReportCallback cb);
    void onPinReportRecv(Demeter::PinReportCallback cb);
    void onSystemReportRecv(Demeter::SystemReportCallback cb);
    void onGetSensorsRecv(Demeter::GetSensorsCallback cb);
    void onRouteAddRecv(Demeter::RouteAddCallback cb);
    void onNackRecv(Demeter::NackCallback cb);
    void onSynRecv(Demeter::AckCallback cb);
    void onSynAckRecv(Demeter::AckCallback cb);

    // --- Configuration ---
    /**
     * @brief Register a static route in the underlying comms strategy.
     * @param id The Node ID.
     * @param mac The MAC Address (6 bytes).
     */
    void registerRoute(uint8_t id, const std::array<uint8_t, 6>& mac);

    // =============================================================
    // SECTION: 2. High-Level Command Senders (Application Layer)
    // =============================================================
    // These methods construct specific commands and call sendFrame()

    /**
     * @brief Send Sensor Data Report (Temp/Hum).
     */
    void sendTempHumReport(uint8_t targetId, const Demeter::TempHumReport& report);

    /**
     * @brief Send Sensor Cluster Report (variable-length plant readings).
     */
    void sendSensorClusterReport(uint8_t targetId, const Demeter::SensorClusterReport& report);

    /**
     * @brief Send GPIO State Report (Feedback).
     */
    void sendPinReport(uint8_t targetId, const Demeter::PinReport& report);

    /**
     * @brief Send System Status Report (Mode, Battery).
     */
    void sendSystemReport(uint8_t targetId, const Demeter::SystemReport& report);
    
    /**
     * @brief Send PING command to check connectivity.
     */
    void sendPing(uint8_t targetId, const Demeter::RequestData& data);
    
    /**
     * @brief Send SYN (Handshake 1/3) compatible with UART/ESP-Now.
     */
    void sendSyn(uint8_t targetId, const Demeter::AckData& data);

    /**
     * @brief Send SYN-ACK (Handshake 2/3).
     */
    void sendSynAck(uint8_t targetId, const Demeter::AckData& data);

    /**
     * @brief Send GPIO Control Command to set a pin state.
     */
    void sendSetGpio(uint8_t targetId, const Demeter::SetGpioCmd& cmd);

    /**
     * @brief Request Sensor Data from a node.
     */
    void sendGetSensors(uint8_t targetId, const Demeter::RequestData& data);

    /**
     * @brief Send Execution Sequence.
     */
    void sendExecSequence(uint8_t targetId, const Demeter::ExecSequenceCmd& cmd);

    /**
     * @brief Send ACK (Acknowledge) response, optionally with Context.
     */
    void sendAck(uint8_t targetId, const Demeter::AckData& data);

private:
    IComms* _strategy;
    uint8_t _myId; // Node ID

    // Callbacks
    Demeter::GpioCallback _onGpioCommand;
    Demeter::PwmCallback _onPwmCommand;
    Demeter::SequenceCallback _onSequenceCommand;
    Demeter::AckCallback _onAckRecv;
    Demeter::PingCallback _onPingRecv;
    Demeter::TempHumReportCallback _onTempHumReportRecv;
    Demeter::SensorClusterReportCallback _onSensorClusterReport;
    Demeter::PinReportCallback    _onPinReport;
    Demeter::SystemReportCallback _onSystemReport;
    Demeter::GetSensorsCallback   _onGetSensors;
    Demeter::RouteAddCallback     _onRouteAdd;
    Demeter::NackCallback         _onNack;
    Demeter::AckCallback _onSynRecv;
    Demeter::AckCallback _onSynAckRecv;

    /**
     * @brief Calculates a simple Modular Sum CRC (Mod 256).
     * @param data Pointer to data buffer.
     * @param len Length of data in bytes.
     * @return uint8_t Calculated CRC.
     */
    uint8_t calculateCRC(const uint8_t* data, size_t len);

    /**
     * @brief Emite una trama genérica de Error o Ausencia Lógica.
     */
    void sendNack(uint8_t targetId);

    /**
     * @brief Desciende estamento lógico a una Trama Binaria y la escupe por COMMS.
     * Envuelve el `payload` crudo anteponiendo el `Header` formateado 
     * (con longitud calculada automáticamente) y posponiendo el `CRC` validado.
     */
    void sendFrame(uint8_t cmdId, uint8_t targetId, const std::vector<uint8_t>& payload);

    /**
     * @brief Lógica profunda de ingesta de Streams de bytes sobre el protocolo.
     * Trocea el frame validando el sincronismo constante, la longitud declarada
     * y el CRC anexo. Si es válido y es para este nodo, avisa al enrutador de CBOR.
     */
    void parseFrame(const std::vector<uint8_t>& frame);
};
