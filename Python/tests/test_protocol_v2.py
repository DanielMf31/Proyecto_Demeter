import sys
import os
import pytest
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import CmdId, SetGpio, Ping

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
