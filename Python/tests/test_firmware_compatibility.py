import pytest
import struct
from proyecto_demeter.config.schemas import TempHumReport, PinReport, SystemReport, CmdId
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2

# Constants from C++ definetion
SYNC_BYTE = 0xFE
HEADER_SIZE = 6

def calculate_crc(data):
    return sum(data) % 256

def create_cpp_frame(cmd_id, payload, src_id=1, dst_id=0):
    # Simulate C++ ProtocolEngine::sendFrame
    header = struct.pack('<BBBBBB', SYNC_BYTE, len(payload), 0x00, src_id, dst_id, cmd_id)
    frame = header + payload
    # CRC over Header[1:] + Payload
    crc = calculate_crc(frame[1:])
    return frame + struct.pack('B', crc)

def test_temphum_report_structure():
    """Verify C++ sendTempHumReport simulation matches Python Parse"""
    # C++ Logic:
    # int16_t t_int = (int16_t)(temp * 100.0f);
    # int16_t h_int = (int16_t)(hum * 100.0f);
    # payload.push_back((uint8_t)(t_int & 0xFF)); ...
    
    temp = 25.43
    hum = 60.55
    
    t_int = int(temp * 100)
    h_int = int(hum * 100)
    
    payload = struct.pack('<hh', t_int, h_int)
    
    # C++ sends TEMP_HUM_REPORT (0x0B)
    frame = create_cpp_frame(0x0B, payload, src_id=10, dst_id=1)
    
    # Python Parse
    protocol = DemeterProtocolV2()
    cmd = protocol.parse_frame(frame)
    
    assert isinstance(cmd, TempHumReport)
    assert cmd.node_id == 10
    assert abs(cmd.temperature - 25.43) < 0.01
    assert abs(cmd.humidity - 60.55) < 0.01

def test_pin_report_structure():
    """Verify C++ sendPinReport simulation matches Python Parse"""
    # C++ Logic:
    # payload.push_back(pin);
    # payload.push_back(state ? 1 : 0);
    
    pin = 13
    state = True
    
    payload = struct.pack('<BB', pin, 1 if state else 0)
    
    # C++ sends PIN_REPORT (0x0C)
    frame = create_cpp_frame(0x0C, payload, src_id=20, dst_id=1)
    
    protocol = DemeterProtocolV2()
    cmd = protocol.parse_frame(frame)
    
    assert isinstance(cmd, PinReport)
    assert cmd.node_id == 20
    assert cmd.pin == 13
    assert cmd.state == 1

def test_system_report_structure():
    """Verify C++ sendSystemReport simulation matches Python Parse"""
    # C++ Logic:
    # [MODE(1)] [BATTERY(2)] [RESERVED(5)]
    
    mode = 2 # DeepSleep
    battery = 3600 # 3.6V
    
    payload = struct.pack('<BH5s', mode, battery, b'\x00'*5)
    
    # C++ sends SYSTEM_REPORT (0x0D)
    frame = create_cpp_frame(0x0D, payload, src_id=30, dst_id=1)
    
    protocol = DemeterProtocolV2()
    cmd = protocol.parse_frame(frame)
    
    assert isinstance(cmd, SystemReport)
    assert cmd.node_id == 30
    assert cmd.mode == 2
    assert cmd.battery_mv == 3600
