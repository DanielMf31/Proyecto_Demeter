import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from proyecto_demeter.Hardware.orchestration.command_dispatcher import GatewayOrchestrator


@pytest.fixture
def orchestrator():
    with patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.UartProcessor'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DemeterWebsocketClient'), \
         patch('proyecto_demeter.Hardware.orchestration.command_dispatcher.DeviceManager'):
        orc = GatewayOrchestrator()
        return orc


@pytest.mark.asyncio
async def test_dispatch_ws_to_uart_set_gpio(orchestrator):
    orchestrator.device_manager.translate_pin.return_value = (2, 4)
    orchestrator.uart.send_command = AsyncMock()

    ws_msg = json.dumps({"type": "set_gpio", "pin": 1, "value": 1})
    await orchestrator.dispatch_ws_to_uart(ws_msg)

    orchestrator.device_manager.translate_pin.assert_called_with(1)
    orchestrator.uart.send_command.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_uart_to_ws_report(orchestrator):
    orchestrator.ws_client.send_json = AsyncMock()

    # Simular un reporte de pin desde un nodo via UART
    from proyecto_demeter.Hardware.orchestration.command_dispatcher import PinReport
    report = PinReport(source_id=2, target_id=1, node_id=2, pin=4, state=1)

    await orchestrator.dispatch_uart_to_ws(report)

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
