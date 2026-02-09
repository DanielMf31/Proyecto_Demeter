from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.shared.schemas import GetSensors, CmdId
import struct

def test_create_get_sensors():
    protocol = DemeterProtocolV2()
    target_id = 2
    
    # 1. Test Factory
    frame = protocol.create_get_sensors(target_id)
    
    assert len(frame) == 7 # Header(6) + Payload(0) + CRC(1) = 7 bytes.
    # Check constants in protocol_v2.py
    # HEADER_FMT = '<BBBBBB' -> 6 bytes
    # Frame = Header + Payload + CRC
    # So 6 + 0 + 1 = 7 bytes.
    
    # Let's decode header
    sync, length, flags, src, dst, cmd = struct.unpack('<BBBBBB', frame[:6])
    
    assert sync == 0xFE
    assert length == 0
    assert dst == target_id
    assert cmd == 0x20 # GET_SENSORS
    
    # Check CRC (Last byte)
    # CRC of Header[1:] + Payload
    # Header[1:] = length, flags, src, dst, cmd (5 bytes)
    # Payload = empty
    # data_to_hash = frame[1:6]
    # sum = 0 + 1 + 0 + 2 + 0x20 = 0x23 (35)
    # CRC = 35 % 256 = 35 (0x23)
    
    crc = frame[6]
    assert crc == 0x23
    print("✅ create_get_sensors test passed")
    
if __name__ == "__main__":
    test_create_get_sensors()
