import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from proyecto_demeter.Hardware.transport.uart_processor import UartProcessor


@pytest.fixture
def uart_processor():
    with patch('proyecto_demeter.Hardware.transport.uart_processor.AsyncUartTransport') as mock_transport:
        mock_transport.return_value.connect = AsyncMock(return_value=True)
        mock_transport.return_value.send = AsyncMock(return_value=True)
        processor = UartProcessor()
        return processor


@pytest.mark.asyncio
async def test_processor_start_stop(uart_processor):
    start_task = asyncio.create_task(uart_processor.start())
    await asyncio.sleep(0.1)

    assert uart_processor.running is True
    assert uart_processor.transport is not None

    await uart_processor.stop()
    assert uart_processor.running is False

    try:
        await asyncio.wait_for(start_task, timeout=1.0)
    except asyncio.TimeoutError:
        pass


@pytest.mark.asyncio
async def test_protocol_internal_ping(uart_processor):
    from proyecto_demeter.Hardware.transport.uart_processor import Ping, Ack, CmdId
    uart_processor.send_command = AsyncMock()

    ping = Ping(source_id=2, target_id=1)
    await uart_processor.handle_protocol_internal(ping)

    uart_processor.send_command.assert_called_once()
    sent_cmd = uart_processor.send_command.call_args[0][0]
    assert isinstance(sent_cmd, Ack)
    assert sent_cmd.target_id == 2
    assert sent_cmd.original_cmd_id == CmdId.PING


@pytest.mark.asyncio
async def test_dispatch_loop_listeners(uart_processor):
    from proyecto_demeter.Hardware.transport.uart_processor import Ping
    mock_listener = AsyncMock()
    uart_processor.add_listener(mock_listener)

    ping = Ping(source_id=2, target_id=1)
    uart_processor.rx_queue.put_nowait(ping)

    dispatch_task = asyncio.create_task(uart_processor._dispatch_loop())
    await asyncio.sleep(0.1)

    mock_listener.assert_called_with(ping)

    dispatch_task.cancel()
    try:
        await dispatch_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_send_helper_methods(uart_processor):
    uart_processor.transport = AsyncMock()
    uart_processor.transport.send = AsyncMock()

    await uart_processor.send_set_gpio(target_id=2, pin=4, value=True)

    uart_processor.transport.send.assert_called_once()
    frame = uart_processor.transport.send.call_args[0][0]
    assert frame[0] == 0xFE  # SYNC byte
