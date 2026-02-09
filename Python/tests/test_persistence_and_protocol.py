import pytest
import os
import json
from proyecto_demeter.config.schemas import SequenceStep, SequenceFile, ExecSequence, SetGpio, Ping, Ack, Nack
from proyecto_demeter.core.sequence_manager import SequenceManager
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2

# --- Test Persistence (JSON) ---

def test_sequence_manager_save_load(tmp_path):
    # Setup
    manager = SequenceManager(directory=str(tmp_path))
    steps = [
        SequenceStep(pin=4, value=1, delay_ms=1000),
        SequenceStep(pin=5, value=0, delay_ms=500)
    ]
    seq_file = SequenceFile(name="Test Routine", description="A test", steps=steps)
    
    # Save
    path = manager.save_sequence("test_p1", seq_file)
    assert os.path.exists(path)
    assert path.endswith("test_p1.json")
    
    # Load
    loaded = manager.load_sequence("test_p1.json")
    assert loaded.name == "Test Routine"
    assert len(loaded.steps) == 2
    assert loaded.steps[0].pin == 4
    assert loaded.steps[1].delay_ms == 500

def test_list_sequences(tmp_path):
    manager = SequenceManager(directory=str(tmp_path))
    # Create empty files
    (tmp_path / "seq1.json").write_text("{}")
    (tmp_path / "seq2.json").write_text("{}")
    (tmp_path / "ignore.txt").write_text("")
    
    files = manager.list_sequences()
    assert len(files) == 2
    assert "seq1.json" in files
    assert "seq2.json" in files

# --- Test Protocol V2 Expansion ---

@pytest.fixture
def protocol():
    return DemeterProtocolV2()

def test_ping_serialization(protocol):
    cmd = Ping(target_id=1)
    frame = protocol.serialize(cmd)
    # Header: FE, Len=01, Target=01, Src=00, Cmd=01(PING), Flags=00
    # Payload: 0 bytes
    # Length of frame: Header(6) + Data(0) + CRC(1) = 7
    assert len(frame) == 7
    assert frame[5] == 0x01 # Cmd ID PING (Index 5)

def test_ack_serialization(protocol):
    # ACK usually sent from Device to Host
    # CmdId.ACK = 0x02
    cmd = Ack(target_id=0, original_cmd_id=0x10)
    frame = protocol.serialize(cmd)
    assert len(frame) == 8 # Header(6) + 1 byte payload + CRC(1)
    assert frame[5] == 0x02 # Cmd ID ACK
    # Payload should be [10]
    assert frame[6] == 0x10

def test_nack_serialization(protocol):
    # CmdId.NACK = 0x03
    cmd = Nack(target_id=0, original_cmd_id=0x10, error_code=0x01)
    frame = protocol.serialize(cmd)
    assert len(frame) == 9 # Header(6) + 2 byte payload + CRC(1)
    assert frame[5] == 0x03 # Cmd ID NACK
    # Payload: [10, 01]
    assert frame[6] == 0x10
    assert frame[7] == 0x01

def test_exec_sequence_full_serialization(protocol):
    steps = [
        SequenceStep(target_id=1, cmd_id=0x10, pin=4, value=1, delay_ms=1000),
        SequenceStep(target_id=1, cmd_id=0x10, pin=5, value=0, delay_ms=500)
    ]
    cmd = ExecSequence(target_id=1, steps=steps)
    frame = protocol.serialize(cmd)
    
    # 6 Header + 1 Count + (2 * 8 Step) + 1 CRC
    expected_len = 6 + 1 + 16 + 1
    assert len(frame) == expected_len
    assert frame[5] == 0x30 # Cmd ID EXEC_SEQUENCE
    assert frame[6] == 0x02 # Step count
