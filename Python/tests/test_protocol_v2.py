import sys
import os
import pytest
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.shared.schemas import CmdId, SetGpio, Ping, DataReport
import struct

class TestProtocolV2:
    def setup_method(self):
        self.protocol = DemeterProtocolV2()

    def test_serialize_set_gpio(self):
        cmd = SetGpio(target_id=1, pin=4, value=1)
        frame = self.protocol.serialize(cmd)
        
        assert frame is not None
        assert frame[0] == 0xFE
        # Frame structure: Sync(1) Len(1) Flags(1) Src(1) Dst(1) Cmd(1) Payload(N) CRC(1)
        # Cmd is at index 5 
        assert frame[5] == CmdId.SET_GPIO

    def test_parse_frame(self):
        cmd = SetGpio(target_id=1, pin=4, value=1)
        frame = self.protocol.serialize(cmd)
        
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, SetGpio)
        assert parsed.pin == 4
        assert parsed.value == 1

    def test_ping(self):
        cmd = Ping(target_id=1)
        frame = self.protocol.serialize(cmd)
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, Ping)

    def test_data_report(self):
        # Create DataReport (Note: Serialization for DataReport is not explicitly implemented in protocol_v2.serialize 
        # because it comes FROM the device, but we can test parsing manually constructed frame)
        
        # Manually construct a valid DataReport frame
        # Payload: Temp=25.43 (2543), Hum=60.12 (6012)
        # [239, 9] [12, 23] (Little Endian)
        t_int = int(25.43 * 100)
        h_int = int(60.12 * 100)
        payload = struct.pack('<hh', t_int, h_int)
        
        # Dst=0 (Host), Cmd=0x0B (DATA_REPORT)
        frame = self.protocol._pack_frame_raw(dst_id=0, cmd_id=CmdId.DATA_REPORT, payload=payload)
        
        parsed = self.protocol.parse_frame(frame)
        assert isinstance(parsed, DataReport)
        assert abs(parsed.temperature - 25.43) < 0.01
        assert abs(parsed.humidity - 60.12) < 0.01
