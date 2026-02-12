import pytest
import pytest_asyncio
import asyncio
from unittest.mock import MagicMock
import sys
import os

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '../src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from proyecto_demeter.transport.mock_transport import MockTransport
from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
from proyecto_demeter.config.schemas import PinReport, CmdId, SetGpio

@pytest.mark.asyncio
async def test_mock_actuator_response():
    # 1. Setup MockTransport in ACTUATOR mode
    transport = MockTransport(mode="ACTUATOR")
    
    # Capture callbacks
    received_frames = []
    def on_data(data):
        received_frames.append(data)
    
    transport.set_callback(on_data)
    await transport.connect()
    
    # 2. Create a SetGpio Command
    protocol = DemeterProtocolV2()
    # Target ID 3 is the simulated actuator in mock_transport.py
    cmd = protocol.serialize(SetGpio(target_id=3, pin=26, value=1))
    
    # 3. Send command to transport (Host -> Transport -> Mock Logic)
    await transport.send(cmd)
    
    # 4. Wait for response (Mock simulates delay)
    await asyncio.sleep(0.5) 
    
    # 5. Verify Response
    assert len(received_frames) > 0, "Actuator did not respond"
    
    # Parse response
    response_frame = received_frames[0]
    parsed = protocol.parse_frame(response_frame)
    
    # Expect PinReport from Actuator
    assert parsed is not None
    assert isinstance(parsed, PinReport)
    assert parsed.get_cmd_id() == CmdId.PIN_REPORT # 0x0C
    assert parsed.node_id == 3
    assert parsed.pin == 26
    assert parsed.state == 1
    
    print("TEST PASSED")
    await transport.close()

if __name__ == "__main__":
    asyncio.run(test_mock_actuator_response())
