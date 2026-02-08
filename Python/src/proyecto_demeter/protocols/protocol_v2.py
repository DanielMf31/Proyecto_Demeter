import struct
import logging
from typing import Optional, Union, Any

from .schemas_protocol import (
    DemeterCommand, 
    SetGpio, 
    SetPwm,
    ExecSequence, 
    RouteAdd, 
    Ping, 
    SequenceStep,
    CmdId
)

# Constants
SYNC_BYTE = 0xFE
HEADER_FMT = '<BBBBBB' 
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SEQUENCE_STEP_FMT = '<BBBBI'
SEQUENCE_STEP_SIZE = struct.calcsize(SEQUENCE_STEP_FMT)

class DemeterProtocolV2:
    """
    Implements the Demeter V2 Binary Protocol.
    
    This class handles the core logic for:
    1.  **Serialization**: Converting High-Level Pydantic Models (`DemeterCommand`) into binary frames.
    2.  **Deserialization**: Parsing incoming binary byte streams into Pydantic Models.
    3.  **Validation**: CRC integrity checks and Frame structure verification.
    
    Frame Structure:
    `[SYNC(1)] [LEN(1)] [FLAGS(1)] [SRC(1)] [DST(1)] [CMD(1)] ... [PAYLOAD(N)] ... [CRC(1)]`
    
    Attributes:
        logger (logging.Logger): Logger instance for protocol events.
    """
    def __init__(self):
        self.logger = logging.getLogger("ProtocolV2")

    def _calculate_crc(self, data: bytes) -> int:
        return sum(data) % 256

    def _pack_frame_raw(self, dst_id: int, cmd_id: int, payload: bytes = b'', flags: int = 0x01) -> bytes:
        src_id = 0x00 # Master ID
        length = len(payload)
        
        header = struct.pack(HEADER_FMT, SYNC_BYTE, length, flags, src_id, dst_id, cmd_id)
        data_to_hash = header[1:] + payload
        crc_val = self._calculate_crc(data_to_hash)
        
        return header + payload + struct.pack('<B', crc_val)

    # ==========================================
    # SERIALIZATION (Model -> Bytes)
    # ==========================================
    def serialize(self, cmd: DemeterCommand) -> bytes:
        payload = b''
        
        if isinstance(cmd, SetGpio):
            # [PIN] [VAL] [FLAGS]
            payload = struct.pack('<BBB', cmd.pin, cmd.value, cmd.flags)

        elif isinstance(cmd, SetPwm):
            # [PIN] [VAL(16)]
            payload = struct.pack('<BH', cmd.pin, cmd.value)
        
        elif isinstance(cmd, ExecSequence):
            # [COUNT] + [Steps...]
            count = len(cmd.steps)
            payload = struct.pack('<B', count)
            for step in cmd.steps:
                step_bytes = struct.pack(SEQUENCE_STEP_FMT, 
                                         step.target_id, 
                                         step.cmd_id,
                                         step.pin, 
                                         step.value, 
                                         step.delay_ms)
                payload += step_bytes
                
        elif isinstance(cmd, RouteAdd):
            # [TARGET_ID] [MAC(6)]
            payload = struct.pack('<B6s', cmd.node_id_to_register, cmd.mac_address_bytes)
            
        elif isinstance(cmd, Ping):
            payload = b''
            
        return self._pack_frame_raw(cmd.target_id, cmd.get_cmd_id(), payload)

    # ==========================================
    # DESERIALIZATION (Bytes -> Model)
    # ==========================================
    def parse_frame(self, frame_bytes: bytes) -> Optional[DemeterCommand]:
        """
        Parses binary frame into a Pydantic Model.
        Returns None if invalid.
        """
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
            # Incomplete frame
            return None
            
        payload = frame_bytes[HEADER_SIZE : HEADER_SIZE+length]
        received_crc = frame_bytes[HEADER_SIZE+length]
        
        # Verify CRC
        data_to_hash = frame_bytes[1 : HEADER_SIZE+length]
        calc_crc = self._calculate_crc(data_to_hash)
        if calc_crc != received_crc:
            self.logger.warning(f"CRC Error. Recv:{received_crc}, Calc:{calc_crc}")
            return None

        # Factory Logic
        try:
            if cmd_id == CmdId.SET_GPIO:
                if len(payload) < 3: return None
                pin, val, flg = struct.unpack('<BBB', payload)
                return SetGpio(target_id=dst, pin=pin, value=val, flags=flg)
                
            elif cmd_id == CmdId.SET_PWM:
                if len(payload) < 3: return None
                pin, val = struct.unpack('<BH', payload)
                return SetPwm(target_id=dst, pin=pin, value=val)

            elif cmd_id == CmdId.PING:
                return Ping(target_id=dst)
                
            elif cmd_id == CmdId.EXEC_SEQUENCE:
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

            # Default/Unknown: Handle generic? 
            # For now return None or implement GenericCommand
            self.logger.info(f"Unknown Command ID: {cmd_id}")
            return None

        except Exception as e:
            self.logger.error(f"Parsing error for cmd {cmd_id}: {e}")
            return None

    # ==========================================
    # HELPERS (Factories)
    # ==========================================
    def create_ping(self, target_id: int) -> bytes:
        return self.serialize(Ping(target_id=target_id))

    def create_set_gpio(self, target_id: int, pin: int, value: int) -> bytes:
        return self.serialize(SetGpio(target_id=target_id, pin=pin, value=value))
