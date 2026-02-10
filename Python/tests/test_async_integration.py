import pytest
import pytest_asyncio
import asyncio
import json
from unittest.mock import MagicMock, AsyncMock
from proyecto_demeter.core.async_service import DemeterService
from proyecto_demeter.transport.interface import TransportStrategy
from proyecto_demeter.transport.protocol_schemas import GpioCommand, PingCommand, SequenceCommand, SequenceStep, ActionResponse

# Mock Transport
class MockAsyncTransport(TransportStrategy):
    def __init__(self):
        self.sent_data = []
        self.callback = None
        self.connected = False

    async def connect(self):
        self.connected = True
        return True

    def start(self): pass
    def stop(self): pass
    async def disconnect(self): self.connected = False

    def set_callback(self, callback):
        self.callback = callback

    async def send(self, data: bytes) -> bool:
        self.sent_data.append(data)
        return True

    async def simulate_rx(self, data: bytes):
        if self.callback:
            self.callback(data)

@pytest.mark.asyncio
async def test_service_gpio_command():
    # Setup
    service = DemeterService()
    service.transport = MockAsyncTransport()
    service.transport.set_callback(service.on_uart_data)
    
    # Mock Protocol to verify calls (or just check transport sent data)
    # We want to check that receiving a JSON TCP command sends bytes to UART
    
    # Create a mock TCP writer
    mock_writer = AsyncMock()
    mock_writer.get_extra_info.return_value = ('127.0.0.1', 12345)
    
    # Manually trigger the logic that would happen inside handle_tcp_client
    # We can't easy call handle_tcp_client without a real reader/writer loop.
    # Instead, let's test the inner logic: _execute_real_gpio
    
    cmd = GpioCommand(pin=2, action="ON")
    await service._execute_real_gpio(cmd)
    
    # Verify Data sent to Transport
    assert len(service.transport.sent_data) == 1
    # Check if data looks like a SetGpio frame (Protocol V2)
    # We can use the service.protocol to verify
    frame = service.transport.sent_data[0]
    parsed = service.protocol.parse_frame(frame)
    assert parsed is not None
    assert parsed.get_cmd_id().value == 0x10 # SET_GPIO
    assert parsed.pin == 2
    assert parsed.value == 1

@pytest.mark.asyncio
async def test_service_ping_command():
    service = DemeterService()
    service.transport = MockAsyncTransport()
    
    # Manually invoke logic (simulating what handle_tcp_client does)
    # Since we can't easily mock the loop, we call the protocol sender directly for verification
    # logic replica:
    cmd = PingCommand(target_id=5)
    payload = service.protocol.create_ping(cmd.target_id)
    await service._send_protocol_cmd(payload)
    
    assert len(service.transport.sent_data) == 1
    parsed = service.protocol.parse_frame(service.transport.sent_data[0])
    assert parsed.get_cmd_id().value == 0x01 # PING
    assert parsed.target_id == 5

@pytest.mark.asyncio
async def test_service_sequence_command():
    service = DemeterService()
    service.transport = MockAsyncTransport()
    
    steps = [SequenceStep(target_id=1, pin=2, value=1, delay_ms=100)]
    cmd = SequenceCommand(steps=steps, target_id=1)
    
    # Simulate processing
    from proyecto_demeter.transport.protocol_schemas import ExecSequence
    exec_seq = ExecSequence(target_id=cmd.target_id, steps=cmd.steps)
    bytes_seq = service.protocol.serialize(exec_seq)
    
    await service._send_protocol_cmd(bytes_seq)
    
    assert len(service.transport.sent_data) == 1
    
    parsed = service.protocol.parse_frame(service.transport.sent_data[0])
    assert parsed.get_cmd_id().value == 0x30 # EXEC_SEQUENCE
    assert len(parsed.steps) == 1
    assert parsed.steps[0].pin == 2
