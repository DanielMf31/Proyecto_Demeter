import pytest
import struct
from proyecto_demeter.shared.protocols.protocol_v2 import DemeterProtocolV2, HEADER_FMT, HEADER_SIZE, SYNC_BYTE
from proyecto_demeter.shared.config.schemas import (
    CmdId, SetGpio, SetPwm, ExecSequence, RouteAdd, Ping, SequenceStep,
    TempHumReport, PinReport, SystemReport, Ack, Nack, Syn, SynAck,
    DemeterCommand
)

class TestProtocolV2:
    def setup_method(self):
        self.protocol = DemeterProtocolV2()

    # ==========================================
    # 1. Serialization Tests (Model -> Bytes)
    # ==========================================

    def test_serialize_ping(self):
        cmd = Ping(target_id=1)
        frame = self.protocol.serialize(cmd)
        
        assert len(frame) == HEADER_SIZE + 0 + 1 # Header + Payload(0) + CRC
        # Header: SYNC(1) LEN(1) FLAGS(1) SRC(1) DST(1) CMD(1)
        assert frame[0] == SYNC_BYTE
        assert frame[1] == 0 # Length
        assert frame[4] == 1 # Dest
        assert frame[5] == CmdId.PING.value

    def test_serialize_ack(self):
        cmd = Ack(target_id=2, original_cmd_id=0x10)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [ORIG_CMD_ID(1)]
        assert frame[1] == 1 
        assert frame[5] == CmdId.ACK.value
        assert frame[6] == 0x10 # Payload byte

    def test_serialize_nack(self):
        cmd = Nack(target_id=2, original_cmd_id=0x10, error_code=0x05)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [ORIG_CMD_ID(1)] [ERR(1)]
        assert frame[1] == 2
        assert frame[5] == CmdId.NACK.value
        assert frame[6] == 0x10
        assert frame[7] == 0x05

    def test_serialize_set_gpio(self):
        cmd = SetGpio(target_id=3, pin=4, value=1)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [PIN(1)] [VAL(1)] [FLAGS(1)]
        assert frame[1] == 3
        assert frame[5] == CmdId.SET_GPIO.value
        assert frame[6] == 4
        assert frame[7] == 1
        assert frame[8] == 0 # Default flags

    def test_serialize_set_pwm(self):
        cmd = SetPwm(target_id=3, pin=5, value=1024)
        frame = self.protocol.serialize(cmd)

        # Payload: [PIN(1)] [VAL(2, LittleEndian)]
        assert frame[1] == 3
        assert frame[6] == 5
        # 1024 -> 0x0400 -> Little Endian: 00 04
        assert frame[7] == 0x00
        assert frame[8] == 0x04

    def test_serialize_route_add(self):
        mac = b'\xAA\xBB\xCC\xDD\xEE\xFF'
        cmd = RouteAdd(target_id=0, node_id_to_register=10, mac_address_bytes=mac)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [NODE_ID(1)] [MAC(6)]
        assert frame[1] == 7
        assert frame[6] == 10
        assert frame[7:13] == mac

    def test_serialize_exec_sequence(self):
        steps = [
            SequenceStep(pin=1, value=1, delay_ms=100),
            SequenceStep(pin=1, value=0, delay_ms=100)
        ]
        cmd = ExecSequence(target_id=5, steps=steps)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [COUNT(1)] + 2 * [STEP(8)]
        # Step: TGT(1) CMD(1) PIN(1) VAL(1) DELAY(4)
        expected_len = 1 + (2 * 8)
        assert frame[1] == expected_len
        assert frame[6] == 2 # Count

    def test_serialize_syn(self):
        cmd = Syn(target_id=1, context=0x01)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [CONTEXT(1)]
        assert frame[1] == 1
        assert frame[5] == CmdId.SYN.value
        assert frame[6] == 0x01

    def test_serialize_syn_ack(self):
        cmd = SynAck(target_id=2, context=0x02)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [CONTEXT(1)]
        assert frame[1] == 1
        assert frame[5] == CmdId.SYN_ACK.value
        assert frame[6] == 0x02

    def test_serialize_system_report(self):
        cmd = SystemReport(target_id=0, node_id=5, mode=1, battery_mv=3700)
        frame = self.protocol.serialize(cmd)
        
        # Payload: [MODE(1)] [BATT(2)] [RESERVED(5)] = 8 bytes
        # Node ID is in Header (Src)
        assert frame[1] == 8
        assert frame[3] == 5 # Src ID (Header index 3)
        assert frame[5] == CmdId.SYSTEM_REPORT.value
        
        # Payload starts at index 6
        assert frame[6] == 1 # Mode
        # 3700 -> 0x0E74 -> LE: 74 0E
        assert frame[7] == 0x74
        assert frame[8] == 0x0E
        assert frame[9:14] == b'\x00\x00\x00\x00\x00'

    # ==========================================
    # 2. Deserialization Tests (Bytes -> Model)
    # ==========================================

    def test_parse_valid_ping(self):
        cmd = Ping(target_id=1)
        frame = self.protocol.serialize(cmd)
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, Ping)
        assert parsed.target_id == 1

    def test_parse_valid_set_gpio(self):
        # Construct Valid Frame manually to test parser isolated from serializer if wanted,
        # but round-trip is better for integration.
        cmd = SetGpio(target_id=10, pin=2, value=0)
        frame = self.protocol.serialize(cmd)
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, SetGpio)
        assert parsed.pin == 2
        assert parsed.value == 0
        assert parsed.target_id == 10
    
    def test_parse_handshake(self):
        # Syn
        cmd = Syn(target_id=1, context=0xAA)
        parsed = self.protocol.parse_frame(self.protocol.serialize(cmd))
        assert isinstance(parsed, Syn)
        assert parsed.context == 0xAA

        # SynAck
        cmd = SynAck(target_id=2, context=0xBB)
        parsed = self.protocol.parse_frame(self.protocol.serialize(cmd))
        assert isinstance(parsed, SynAck)
        assert parsed.context == 0xBB

    def test_parse_reports(self):
        # TempHum
        cmd = TempHumReport(target_id=0, node_id=5, temperature=20.5, humidity=50.0)
        parsed = self.protocol.parse_frame(self.protocol.serialize(cmd))
        assert isinstance(parsed, TempHumReport)
        assert parsed.node_id == 5
        assert parsed.temperature == 20.5

        # PinReport
        cmd = PinReport(target_id=0, node_id=3, pin=4, state=1)
        parsed = self.protocol.parse_frame(self.protocol.serialize(cmd))
        assert isinstance(parsed, PinReport)
        assert parsed.state == 1
        
        # SystemReport
        cmd = SystemReport(target_id=0, node_id=7, mode=2, battery_mv=4200)
        parsed = self.protocol.parse_frame(self.protocol.serialize(cmd))
        assert isinstance(parsed, SystemReport)
        assert parsed.node_id == 7
        assert parsed.mode == 2
        assert parsed.battery_mv == 4200

    def test_demeter_command_base(self):
        # Ensure base class validation works (e.g. invalid target_id)
        with pytest.raises(ValueError):
            Ping(target_id=300) # Max 254
            
        # Ensure abstract method raises error
        base = DemeterCommand(target_id=1)
        with pytest.raises(NotImplementedError):
            base.get_cmd_id()

    # ==========================================
    # 3. Edge Cases & Error Handling
    # ==========================================

    def test_crc_failure(self):
        cmd = Ping(target_id=1)
        frame = bytearray(self.protocol.serialize(cmd))
        
        # Corrupt CRC (Test standard CRC failure)
        frame[-1] = (frame[-1] + 1) % 256
        
        assert self.protocol.parse_frame(frame) is None

    def test_incomplete_frame(self):
        cmd = SetGpio(target_id=1, pin=1, value=1)
        frame = self.protocol.serialize(cmd)
        
        # Cut off last byte (CRC)
        incomplete = frame[:-1]
        assert self.protocol.parse_frame(incomplete) is None
        
        # Cut off payload
        incomplete = frame[:HEADER_SIZE]
        assert self.protocol.parse_frame(incomplete) is None

    def test_garbage_data(self):
        garbage = b'\x00\xFF\xAA\xBB\xCC'
        assert self.protocol.parse_frame(garbage) is None
        
        # Valid SYNC but garbage rest
        garbage_sync = b'\xFE\x00\x00\x00\x00\x00\x00\x00' # Correct length header but invalid CRC likely
        assert self.protocol.parse_frame(garbage_sync) is None

    def test_unknown_cmd_id(self):
        # Manually construct frame with unknown CMD ID 0xFF
        # Header: SYNC(1) LEN(1) FLAGS(1) SRC(1) DST(1) CMD(1)
        payload = b''
        header = struct.pack(HEADER_FMT, SYNC_BYTE, 0, 0, 0, 1, 0xFF)
        # Calculate CRC manually or use helper if exposed, 
        # but _calculate_crc is internal. We can use the public serialize method of a "Fake" command or access private.
        
        # Let's verify _calculate_crc logic indirectly or access it.
        # Accessing protected member for test setup is acceptable in unit tests.
        crc_val = self.protocol._calculate_crc(header[1:] + payload)
        frame = header + payload + struct.pack('<B', crc_val)
        
        parsed = self.protocol.parse_frame(frame)
        assert parsed is None # Should log unknown command and return None

    def test_zero_length_payload_command(self):
        # Ping has zero length
        cmd = Ping(target_id=1)
        frame = self.protocol.serialize(cmd)
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, Ping)
