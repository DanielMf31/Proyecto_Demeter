import sys
import os
import pytest
import struct

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import (
    CmdId, SetGpio, SetPwm, ExecSequence, RouteAdd, Ping, SequenceStep,
    TempHumReport, PinReport, SystemReport
)

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
        assert frame[5] == CmdId.SET_GPIO.value

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

    def test_temphum_report(self):
        # Model -> Bytes
        cmd = TempHumReport(target_id=0, node_id=10, temperature=24.5, humidity=50.2)
        serialized = self.protocol.serialize(cmd)
        
        # Bytes -> Model
        parsed = self.protocol.parse_frame(serialized)
        assert isinstance(parsed, TempHumReport)
        assert parsed.node_id == 10
        assert abs(parsed.temperature - 24.5) < 0.05 # Precision loss due to int16 packing
        assert abs(parsed.humidity - 50.2) < 0.05

    def test_pin_report(self):
        # Model -> Bytes
        cmd = PinReport(target_id=0, node_id=3, pin=26, state=1)
        serialized = self.protocol.serialize(cmd)
        
        # Bytes -> Model
        parsed = self.protocol.parse_frame(serialized)
        assert isinstance(parsed, PinReport)
        assert parsed.node_id == 3
        assert parsed.pin == 26
        assert parsed.state == 1

    def test_system_report(self):
        # Model -> Bytes
        cmd = SystemReport(target_id=0, node_id=3, mode=1, battery_mv=12500)
        serialized = self.protocol.serialize(cmd)
        
        # Bytes -> Model
        parsed = self.protocol.parse_frame(serialized)
        assert isinstance(parsed, SystemReport)
        assert parsed.node_id == 3
        assert parsed.mode == 1
        assert parsed.battery_mv == 12500
        assert parsed.reserved == b'\x00\x00\x00\x00\x00'
