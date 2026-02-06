import struct
import logging
from typing import Union
from .schemas_protocol import (
    DemeterCommand, 
    SetGpio, 
    ExecSequence, 
    RouteAdd, 
    Ping, 
    SequenceStep,
    CmdId
)

# ==========================================
# 1. CONSTANTS definitions handled in Enums/Schemas now
#    But we keep HEADER_FMT for internal packing
# ==========================================

SYNC_BYTE = 0xFE
HEADER_FMT = '<BBBBBB' 
HEADER_SIZE = struct.calcsize(HEADER_FMT)
SEQUENCE_STEP_FMT = '<BBBBI'

# Re-export constants for compatibility
CMD_PING = CmdId.PING.value
CMD_ACK = CmdId.ACK.value
CMD_NACK = CmdId.NACK.value
CMD_SET_GPIO = CmdId.SET_GPIO.value
CMD_EXEC_SEQUENCE = CmdId.EXEC_SEQUENCE.value
CMD_REPORT_BATCH = CmdId.REPORT_BATCH.value

class DemeterProtocolV2:
    """
    Implements the Demeter V2 Binary Protocol.
    Now powered by Pydantic Schemas for validation.
    """
    def __init__(self):
        self.logger = logging.getLogger("ProtocolV2")

    def _calculate_crc(self, data: bytes) -> int:
        return sum(data) % 256

    def _pack_frame_raw(self, dst_id: int, cmd_id: int, payload: bytes = b'', flags: int = 0x01) -> bytes:
        """Internal worker: Just bytes in, bytes out."""
        src_id = 0x00 # Master ID
        length = len(payload)
        
        header = struct.pack(HEADER_FMT, SYNC_BYTE, length, flags, src_id, dst_id, cmd_id)
        data_to_hash = header[1:] + payload
        crc_val = self._calculate_crc(data_to_hash)
        
        return header + payload + struct.pack('<B', crc_val)

    # ==========================================
    # NEW API: SERIALIZE
    # ==========================================
    def serialize(self, cmd: DemeterCommand) -> bytes:
        """
        Universal serializer for any DemeterCommand model.
        """
        payload = b''
        
        if isinstance(cmd, SetGpio):
            # [PIN] [VAL] [FLAGS]
            payload = struct.pack('<BBB', cmd.pin, cmd.value, cmd.flags)
        
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
    # LEGACY / CONVENIENCE HELPERS (Wrappers)
    # ==========================================

    def create_ping(self, target_id: int) -> bytes:
        return self.serialize(Ping(target_id=target_id))

    def create_set_gpio(self, target_id: int, pin: int, value: int) -> bytes:
        return self.serialize(SetGpio(target_id=target_id, pin=pin, value=value))

    def create_route_add(self, target_node_id: int, mac_bytes: bytes) -> bytes:
        # RouteAdd is usually sent to Gateway (ID 1)
        # But payload contains the node ID being registered
        return self.serialize(RouteAdd(target_id=1, node_id_to_register=target_node_id, mac_address_bytes=mac_bytes))

    def create_sequence(self, steps: list) -> bytes:
        # Convert legacy dict list to Pydantic models
        pydantic_steps = []
        # Target usually ID 1 (Gateway) for orchestration, or specific node
        # We assume Gateway ID 1 for the main frame
        
        for s in steps:
            pydantic_steps.append(SequenceStep(
                target_id=s['target'],
                cmd_id=s.get('cmd', CmdId.SET_GPIO.value),
                pin=s['pin'],
                value=s['val'],
                delay_ms=s['delay']
            ))
            
        seq = ExecSequence(target_id=1, steps=pydantic_steps)
        return self.serialize(seq)

    # ==========================================
    # PARSING
    # ==========================================
    def parse_frame(self, frame_bytes: bytes):
        """Standard parser (unchanged logic, just moved helpers)."""
        if len(frame_bytes) < HEADER_SIZE + 1:
            return None
        try:
            sync, length, flags, src, dst, cmd = struct.unpack(HEADER_FMT, frame_bytes[:HEADER_SIZE])
        except struct.error:
            return None
            
        if sync != SYNC_BYTE:
            return None
            
        expected_total_len = HEADER_SIZE + length + 1
        if len(frame_bytes) < expected_total_len:
            return None
            
        payload = frame_bytes[HEADER_SIZE : HEADER_SIZE+length]
        received_crc = frame_bytes[HEADER_SIZE+length]
        
        data_to_hash = frame_bytes[1 : HEADER_SIZE+length]
        calc_crc = self._calculate_crc(data_to_hash)
        
        if calc_crc != received_crc:
            self.logger.warning(f"CRC Mismatch! Recv: {received_crc}, Calc: {calc_crc}")
            return None
            
        return {
            "src": src,
            "dst": dst,
            "cmd": cmd,
            "payload": payload,
            "flags": flags
        }
