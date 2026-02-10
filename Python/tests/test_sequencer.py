import pytest
import struct
from proyecto_demeter.transport.protocol_schemas import SequenceStep, ExecSequence
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2

def test_sequence_step_validation():
    # Valid Step
    step = SequenceStep(pin=4, value=1, delay_ms=1000)
    assert step.pin == 4
    assert step.value == 1
    assert step.delay_ms == 1000

    # Invalid Pin (New limit < 0)
    # But Pydantic validates ge=0. 
    with pytest.raises(ValueError):
        SequenceStep(pin=-1, value=1, delay_ms=100)

    # Invalid Pin (New limit > 40)
    with pytest.raises(ValueError):
        SequenceStep(pin=41, value=1, delay_ms=100)
        
    # Invalid Value (not 0 or 1)
    with pytest.raises(ValueError):
        SequenceStep(pin=4, value=2, delay_ms=100)
        
    # Invalid Delay (< 0) - Although model says ge=0, typical is >0, but 0 is technically allowed for no delay?
    # Schema says ge=0.
    # Check negative
    with pytest.raises(ValueError):
        SequenceStep(pin=4, value=1, delay_ms=-1)

def test_exec_sequence_serialization():
    protocol = DemeterProtocolV2()
    
    # Create Protocol Steps (Low Level)
    steps = [
        SequenceStep(target_id=1, cmd_id=0x10, pin=4, value=1, delay_ms=500),
        SequenceStep(target_id=1, cmd_id=0x10, pin=4, value=0, delay_ms=500)
    ]
    
    cmd = ExecSequence(target_id=1, steps=steps)
    frame = protocol.serialize(cmd)
    
    # Validation
    # Header (7) + Count (1) + Steps (2 * 8) + CRC (1) = 25 bytes
    # Wait, Payload structure for EXEC_SEQUENCE:
    # [COUNT] [STEP1...] [STEP2...]
    # Step: TGT(1) CMD(1) PIN(1) VAL(1) DELAY(4) = 8 bytes
    
    assert len(frame) == 6 + 1 + 16 + 1
    
    # Check Header CMD_ID (0x30 = 48)
    # Header: SYNC(1) LEN(1) FLAGS(1) SRC(1) DST(1) CMD(1)
    # Frame[5] is CMD
    assert frame[5] == 0x30
    
    # Check Payload Count
    # Payload starts at index 6
    assert frame[6] == 2 # 2 steps
