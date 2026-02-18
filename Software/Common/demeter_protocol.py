import struct
import logging
from typing import Optional, Union, Any, Dict, Type

from schemas import (
    DemeterCommand, 
    SetGpio, 
    SetPwm,
    ExecSequence, 
    RouteAdd, 
    Ping, 
    SequenceStep,
    Ack,
    Nack,
    Syn,
    SynAck,
    CmdId,
    TempHumReport,
    PinReport,
    SystemReport,
    GetSensors
)

# Constants
SYNC_BYTE = 0xFE
HEADER_FMT = '<BBBBBB' 
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SEQUENCE_STEP_FMT = '<BBBBI'
SEQUENCE_STEP_SIZE = struct.calcsize(SEQUENCE_STEP_FMT)

class DemeterProtocolV2:
    """
    Implements the Demeter V2 Binary Protocol with Registry Pattern.
    """
    def __init__(self):
        self.logger = logging.getLogger("ProtocolV2")
        self._registry: Dict[int, Any] = {
            CmdId.PING: self._parse_ping,
            CmdId.ACK: self._parse_ack,
            CmdId.NACK: self._parse_nack,
            CmdId.SYN: self._parse_syn,
            CmdId.SYN_ACK: self._parse_syn_ack,
            CmdId.SET_GPIO: self._parse_set_gpio,
            CmdId.SET_PWM: self._parse_set_pwm,
            CmdId.EXEC_SEQUENCE: self._parse_exec_sequence,
            CmdId.TEMP_HUM_REPORT: self._parse_temp_hum_report,
            CmdId.PIN_REPORT: self._parse_pin_report,
            CmdId.SYSTEM_REPORT: self._parse_system_report
        }

    def _calculate_crc(self, data: bytes) -> int:
        return sum(data) % 256

    def pack_frame(self, cmd: DemeterCommand) -> bytes:
        """
        Serialize a DemeterCommand into a binary frame.
        """
        # 1. Serialize Payload
        payload = b''
        src_id = cmd.source_id if cmd.source_id is not None else 0x00
        cmd_id = cmd.get_cmd_id()

        if isinstance(cmd, SetGpio):
            payload = struct.pack('<BBB', cmd.pin, cmd.value, cmd.flags)
        elif isinstance(cmd, SetPwm):
            payload = struct.pack('<BH', cmd.pin, cmd.value)
        elif isinstance(cmd, ExecSequence):
            count = len(cmd.steps)
            payload = struct.pack('<B', count)
            for step in cmd.steps:
                payload += struct.pack(SEQUENCE_STEP_FMT, step.target_id, step.cmd_id, step.pin, step.value, step.delay_ms)
        elif isinstance(cmd, RouteAdd):
            payload = struct.pack('<B6s', cmd.node_id_to_register, cmd.mac_address_bytes)
        elif isinstance(cmd, Ack):
            payload = struct.pack('<B', cmd.original_cmd_id)
        elif isinstance(cmd, Nack):
            payload = struct.pack('<BB', cmd.original_cmd_id, cmd.error_code)
        elif isinstance(cmd, (Syn, SynAck)):
            payload = struct.pack('<B', cmd.context)
        elif isinstance(cmd, TempHumReport):
            t_int = int(cmd.temperature * 100)
            h_int = int(cmd.humidity * 100)
            payload = struct.pack('<hh', t_int, h_int)
        elif isinstance(cmd, PinReport):
            payload = struct.pack('<BB', cmd.pin, cmd.state)
        elif isinstance(cmd, SystemReport):
            payload = struct.pack('<BH5s', cmd.mode, cmd.battery_mv, cmd.reserved)
        # Ping, GetSensors have empty payload

        # 2. Pack Header & CRC
        length = len(payload)
        flags = 0x01 # Default flags
        dst_id = cmd.target_id
        
        header = struct.pack(HEADER_FMT, SYNC_BYTE, length, flags, src_id, dst_id, cmd_id)
        data_to_hash = header[1:] + payload
        crc_val = self._calculate_crc(data_to_hash)
        
        return header + payload + struct.pack('<B', crc_val)

    def validate_json_message(self, json_data: Dict[str, Any]) -> DemeterCommand:
        """
        Validate a generic JSON dictionary against known Command Models.
        Returns a specific DemeterCommand instance or raises ValidationError.
        """
        cmd_type = json_data.get("command")
        params = json_data.get("params", {})
        
        # Mappings for JSON commands to Pydantic Models
        # This handles the "Standard" JSON format -> Internal Pydantic Model
        if cmd_type == "TOGGLE_PIN":
            # Map params: gpio -> pin, state -> value
            state_val = 1 if params.get("state") == "ON" else 0
            return SetGpio(
                target_id=params.get("target_id", 1), # Default to node 1 if not specified
                pin=params.get("gpio"),
                value=state_val
            )
        
        if cmd_type == "PING":
             return Ping(target_id=params.get("target_id", 1))

        raise ValueError(f"Unknown command type: {cmd_type}")

    # ==========================================
    # DESERIALIZATION (Bytes -> Model)
    # ==========================================
    def parse_frame(self, frame_bytes: bytes) -> Optional[DemeterCommand]:
        if len(frame_bytes) < HEADER_SIZE + 1:
            return None
        
        try:
            sync, length, flags, src, dst, cmd_id = struct.unpack(HEADER_FMT, frame_bytes[:HEADER_SIZE])
        except struct.error:
            return None
            
        if sync != SYNC_BYTE:
            return None
            
        expected_total_len = HEADER_SIZE + length + 1
        if len(frame_bytes) < expected_total_len:
            return None
            
        payload = frame_bytes[HEADER_SIZE : HEADER_SIZE+length]
        received_crc = frame_bytes[HEADER_SIZE+length]
        
        # Verify CRC
        calc_crc = self._calculate_crc(frame_bytes[1 : HEADER_SIZE+length])
        if calc_crc != received_crc:
            self.logger.warning(f"CRC Error: Calc={calc_crc:02X} Recv={received_crc:02X} | Data={frame_bytes.hex()}")
            return None

        # Registry Dispatch
        parser = self._registry.get(cmd_id)
        if parser:
            cmd = parser(dst, src, payload)
            if cmd:
                cmd.source_id = src
            return cmd
        
        self.logger.info(f"Unknown Command ID: 0x{cmd_id:02X}")
        return None

    # --- Parsers ---
    def _parse_ping(self, dst, src, payload):
        return Ping(target_id=dst)

    def _parse_ack(self, dst, src, payload):
        if len(payload) < 1: return None
        return Ack(target_id=dst, original_cmd_id=payload[0])

    def _parse_nack(self, dst, src, payload):
        if len(payload) < 2: return None
        orig, err = struct.unpack('<BB', payload)
        return Nack(target_id=dst, original_cmd_id=orig, error_code=err)

    def _parse_syn(self, dst, src, payload):
        ctx = payload[0] if len(payload) > 0 else 0
        return Syn(target_id=dst, context=ctx)

    def _parse_syn_ack(self, dst, src, payload):
        ctx = payload[0] if len(payload) > 0 else 0
        return SynAck(target_id=dst, context=ctx)

    def _parse_set_gpio(self, dst, src, payload):
        if len(payload) < 3: return None
        pin, val, flg = struct.unpack('<BBB', payload)
        return SetGpio(target_id=dst, pin=pin, value=val, flags=flg)

    def _parse_set_pwm(self, dst, src, payload):
        if len(payload) < 3: return None
        pin, val = struct.unpack('<BH', payload)
        return SetPwm(target_id=dst, pin=pin, value=val)

    def _parse_exec_sequence(self, dst, src, payload):
        if len(payload) < 1: return None
        count = payload[0]
        steps = []
        offset = 1
        for _ in range(count):
            if offset + SEQUENCE_STEP_SIZE > len(payload): break
            tgt, c_id, p, v, d = struct.unpack(SEQUENCE_STEP_FMT, payload[offset:offset+SEQUENCE_STEP_SIZE])
            steps.append(SequenceStep(target_id=tgt, cmd_id=c_id, pin=p, value=v, delay_ms=d))
            offset += SEQUENCE_STEP_SIZE
        return ExecSequence(target_id=dst, steps=steps)

    def _parse_temp_hum_report(self, dst, src, payload):
        if len(payload) < 4: return None
        t_int, h_int = struct.unpack('<hh', payload)
        return TempHumReport(target_id=dst, node_id=src, temperature=t_int/100.0, humidity=h_int/100.0)

    def _parse_pin_report(self, dst, src, payload):
        if len(payload) < 2: return None
        pin, state = struct.unpack('<BB', payload)
        return PinReport(target_id=dst, node_id=src, pin=pin, state=state)

    def _parse_system_report(self, dst, src, payload):
        if len(payload) < 8: return None
        mode, batt_mv, reserved = struct.unpack('<BH5s', payload)
        return SystemReport(target_id=dst, node_id=src, mode=mode, battery_mv=batt_mv, reserved=reserved)

    # --- Helpers ---
    def create_ping(self, target_id: int) -> bytes:
        return self.pack_frame(Ping(target_id=target_id))
