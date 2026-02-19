import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from proyecto_demeter.Hardware.orchestration.command_dispatcher import GatewayOrchestrator
from schemas import SetGpio, Ack, PinReport

@pytest.fixture
def orchestrator():
    with patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.UartProcessor'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DemeterWebsocketClient'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DeviceManager'):
        orc = GatewayOrchestrator()
        return orc

@pytest.mark.asyncio
async def test_dispatch_ws_to_uart_set_gpio(orchestrator):
    # Mock DeviceManager to return a known mapping
    orchestrator.device_manager.translate_pin.return_value = (2, 4)
    orchestrator.uart.send_command = AsyncMock()
    
    # Message from WS/Frontend: set logical pump 1 ON
    ws_msg = json.dumps({
        "type": "set_gpio",
        "pin": 1,
        "value": 1
    })
    
    await orchestrator.dispatch_ws_to_uart(ws_msg)
    
    # Verify translation occurred
    orchestrator.device_manager.translate_pin.assert_called_with(1)
    
    # Verify UART command was sent with translated values
    orchestrator.uart.send_command.assert_called_once()
    cmd = orchestrator.uart.send_command.call_args[0][0]
    assert isinstance(cmd, SetGpio)
    assert cmd.target_id == 2
    assert cmd.pin == 4
    assert cmd.value == 1

@pytest.mark.asyncio
async def test_dispatch_uart_to_ws_report(orchestrator):
    orchestrator.ws_client.send_json = AsyncMock()
    
    # Message from Node via UART: Pin 4 changed to state 1
    report = PinReport(source_id=2, target_id=1, node_id=2, pin=4, state=1)
    
    await orchestrator.dispatch_uart_to_ws(report)
    
    # Verify it was forwarded to WS
    orchestrator.ws_client.send_json.assert_called_once()
    payload = orchestrator.ws_client.send_json.call_args[0][0]
    assert payload["type"] == "pin_report"
    assert payload["node_id"] == 2
    assert payload["pin"] == 4
    assert payload["state"] == 1

@pytest.mark.asyncio
async def test_report_system_config(orchestrator):
    orchestrator.ws_client.send_json = AsyncMock()
    orchestrator.device_manager.get_config.return_value = {"pump": {"1": {"target_id": 1}}}
    
    await orchestrator.report_system_config()
    
    orchestrator.ws_client.send_json.assert_called_once()
    payload = orchestrator.ws_client.send_json.call_args[0][0]
    assert payload["type"] == "system_config"
    assert "pump" in payload["devices"]
