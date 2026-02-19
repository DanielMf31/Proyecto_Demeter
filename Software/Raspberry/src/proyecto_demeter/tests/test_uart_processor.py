import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from proyecto_demeter.Hardware.transport.uart_processor import UartProcessor
from demeter_protocol import DemeterProtocolV2
from schemas import Ping, Ack, TempHumReport, CmdId

@pytest.fixture
def uart_processor():
    with patch('proyecto_demeter.Hardware.transport.uart_processor.AsyncUartTransport') as mock_transport:
        mock_transport.return_value.connect = AsyncMock(return_value=True)
        mock_transport.return_value.send = AsyncMock(return_value=True)
        processor = UartProcessor()
        return processor

@pytest.mark.asyncio
async def test_processor_start_stop(uart_processor):
    # Start in a background task
    start_task = asyncio.create_task(uart_processor.start())
    await asyncio.sleep(0.1) # Let it initialize
    
    assert uart_processor.running is True
    assert uart_processor.transport is not None
    
    await uart_processor.stop()
    assert uart_processor.running is False
    
    try:
        await asyncio.wait_for(start_task, timeout=1.0)
    except asyncio.TimeoutError:
        pass # Expected if it doesn't stop immediately, but stop() should handle it

@pytest.mark.asyncio
async def test_process_valid_frame(uart_processor):
    protocol = DemeterProtocolV2()
    ping = Ping(source_id=2, target_id=1)
    frame = protocol.pack_frame(ping)
    
    # Simulate receiving data
    uart_processor.on_uart_data(frame)
    
    # Check if command is in queue
    cmd = await uart_processor.rx_queue.get()
    assert isinstance(cmd, Ping)
    assert cmd.source_id == 2

@pytest.mark.asyncio
async def test_protocol_internal_ping(uart_processor):
    # Mock send_command to verify it replies to PING
    uart_processor.send_command = AsyncMock()
    
    ping = Ping(source_id=2, target_id=1)
    await uart_processor.handle_protocol_internal(ping)
    
    # Should send an ACK for PING
    uart_processor.send_command.assert_called_once()
    sent_cmd = uart_processor.send_command.call_args[0][0]
    assert isinstance(sent_cmd, Ack)
    assert sent_cmd.target_id == 2
    assert sent_cmd.original_cmd_id == CmdId.PING

@pytest.mark.asyncio
async def test_dispatch_loop_listeners(uart_processor):
    mock_listener = AsyncMock()
    uart_processor.add_listener(mock_listener)
    
    ping = Ping(source_id=2, target_id=1)
    uart_processor.rx_queue.put_nowait(ping)
    
    # Start dispatch loop task
    dispatch_task = asyncio.create_task(uart_processor._dispatch_loop())
    
    await asyncio.sleep(0.1) # Let it process
    
    mock_listener.assert_called_with(ping)
    
    dispatch_task.cancel()
    try: await dispatch_task
    except asyncio.CancelledError: pass

@pytest.mark.asyncio
async def test_send_helper_methods(uart_processor):
    uart_processor.transport = AsyncMock()
    uart_processor.transport.send = AsyncMock()
    
    await uart_processor.send_set_gpio(target_id=2, pin=4, value=True)
    
    # Verify transport.send was called with a frame
    uart_processor.transport.send.assert_called_once()
    frame = uart_processor.transport.send.call_args[0][0]
    assert frame[0] == 0xFE # SYNC
