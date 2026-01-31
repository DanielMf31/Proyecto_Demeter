import struct
import logging

# ==========================================
# 1. CONSTANTS & DEFINITIONS
# ==========================================

# Sync Byte
SYNC_BYTE = 0xFE

# Command IDs
CMD_PING            = 0x01
CMD_ACK             = 0x02
CMD_NACK            = 0x03
CMD_HELLO           = 0x04 # Device Discovery
CMD_ROUTE_ADD       = 0x0A # Gateway Routing Table Update
CMD_SET_GPIO        = 0x10
CMD_SET_PWM         = 0x11
CMD_GET_SENSORS     = 0x20
CMD_REPORT_SINGLE   = 0x21
CMD_REPORT_BATCH    = 0x22
CMD_EXEC_SEQUENCE   = 0x30

# Header Format: < (Little Endian)
# B=Sync, B=Len, B=Flags, B=Src, B=Dst, B=Cmd
HEADER_FMT = '<BBBBBB' 
HEADER_SIZE = struct.calcsize(HEADER_FMT)

# Sequence Step Format: 
# Target(1), Cmd(1), Pin(1), Val(1), Delay(4)
# <BBBBI
SEQUENCE_STEP_FMT = '<BBBBI'

class DemeterProtocolV2:
    """
    Implements the Demeter V2 Binary Protocol.
    Handles packing (Serialization) and unpacking (Deserialization) of frames.
    """
    def __init__(self):
        self.logger = logging.getLogger("ProtocolV2")
        self.seq_counter = 0

    def _calculate_crc(self, data: bytes) -> int:
        """
        Simple Checksum (Sum of bytes) mod 256 for MVP.
        In production, replace with proper CRC8-CCITT.
        """
        return sum(data) % 256

    def _pack_frame(self, dst_id: int, cmd_id: int, payload: bytes = b'', flags: int = 0x01) -> bytes:
        """
        Constructs the full binary frame.
        Flags: 0x01 = ACK Requested by default.
        """
        src_id = 0x00 # Master ID
        length = len(payload)
        
        # 1. Header
        header = struct.pack(HEADER_FMT, SYNC_BYTE, length, flags, src_id, dst_id, cmd_id)
        
        # 2. Calculate CRC (Only over Header fields [except Sync?] + Payload)
        # PRD says: CRC(LEN + FLAGS + SRC + DST + CMD + PAYLOAD)
        # So we skip index 0 (SYNC)
        data_to_hash = header[1:] + payload
        crc_val = self._calculate_crc(data_to_hash)
        
        # 3. Assemble
        frame = header + payload + struct.pack('<B', crc_val)
        return frame

    # ==========================================
    # COMMAND GENERATORS
    # ==========================================

    def create_ping(self, target_id: int) -> bytes:
        return self._pack_frame(target_id, CMD_PING)

    def create_set_gpio(self, target_id: int, pin: int, value: int) -> bytes:
        """
        Payload: [PIN] [VAL] [FLAGS]
        """
        payload = struct.pack('<BBB', pin, value, 0)
        return self._pack_frame(target_id, CMD_SET_GPIO, payload)

    def create_route_add(self, target_node_id: int, mac_bytes: bytes) -> bytes:
        """
        Payload: [TARGET_ID (1)] [MAC (6)]
        Sent to Gateway (ID 1) usually.
        """
        # MAC bytes should be length 6
        if len(mac_bytes) != 6:
             raise ValueError("MAC Address must be 6 bytes")
        
        payload = struct.pack('<B6s', target_node_id, mac_bytes)
        # We send this command TO THE GATEWAY (usually ID 1), telling it about target_node_id
        # But wait, the DST_ID of the FRAME is the Gateway. 
        # The Payload contains the ID we are registering.
        return self._pack_frame(1, CMD_ROUTE_ADD, payload) 

    def create_sequence(self, steps: list) -> bytes:
        """
        Creates a batch sequence command.
        steps: List of dictionaries {'target':, 'cmd':, 'pin':, 'val':, 'delay':}
        Payload: [COUNT (1)] + [Step1 (8)] + [Step2 (8)]...
        """
        count = len(steps)
        payload = struct.pack('<B', count)
        
        for step in steps:
            # Struct: Target(1), Cmd(1), Pin(1), Val(1), Delay(4)
            step_bytes = struct.pack(SEQUENCE_STEP_FMT, 
                                     step['target'], 
                                     step['cmd'],    # e.g. CMD_SET_GPIO
                                     step['pin'], 
                                     step['val'], 
                                     step['delay'])
            payload += step_bytes
            
        # Send to Gateway (ID 1)
        return self._pack_frame(1, CMD_EXEC_SEQUENCE, payload)

    # ==========================================
    # PARSING LOGIC
    # ==========================================
    
    def parse_frame(self, frame_bytes: bytes):
        """
        Parses a complete frame. 
        Returns dict or None if invalid.
        """
        if len(frame_bytes) < HEADER_SIZE + 1: # Header + CRC min
            return None
            
        # Unpack Header
        try:
            sync, length, flags, src, dst, cmd = struct.unpack(HEADER_FMT, frame_bytes[:HEADER_SIZE])
        except struct.error:
            return None
            
        if sync != SYNC_BYTE:
            return None
            
        expected_total_len = HEADER_SIZE + length + 1
        if len(frame_bytes) < expected_total_len:
            return None # Incomplete frame
            
        # Extract payload and CRC
        payload = frame_bytes[HEADER_SIZE : HEADER_SIZE+length]
        received_crc = frame_bytes[HEADER_SIZE+length]
        
        # Verify CRC
        data_to_hash = frame_bytes[1 : HEADER_SIZE+length] # Skip Sync, include header+payload
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
