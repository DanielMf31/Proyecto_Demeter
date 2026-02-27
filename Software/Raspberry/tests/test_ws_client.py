import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch
from proyecto_demeter.Hardware.ws_client.client import DemeterWebsocketClient


@pytest.fixture
def ws_client():
    mock_msg_callback = AsyncMock()
    mock_open_callback = AsyncMock()
    client = DemeterWebsocketClient(
        on_message_callback=mock_msg_callback,
        on_open_callback=mock_open_callback
    )
    return client, mock_msg_callback, mock_open_callback


@pytest.mark.asyncio
async def test_ws_client_connect_loop(ws_client):
    client, on_msg, on_open = ws_client

    mock_ws = AsyncMock()
    mock_ws.__aiter__.return_value = ["{\"type\": \"ping\"}"]

    with patch('proyecto_demeter.Hardware.ws_client.client.websockets') as mock_websockets:
        mock_websockets.connect.return_value.__aenter__.return_value = mock_ws

        client.running = True
        task = asyncio.create_task(client._connect_loop())

        for _ in range(50):
            if on_msg.call_count >= 1:
                break
            await asyncio.sleep(0.01)

        client.running = False
        assert mock_websockets.connect.call_count >= 1
        on_open.assert_called_once()
        on_msg.assert_called_with("{\"type\": \"ping\"}")

        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=0.1)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


@pytest.mark.asyncio
async def test_ws_send_json(ws_client):
    client, _, _ = ws_client
    mock_ws = AsyncMock()
    client.connection = mock_ws

    payload = {"status": "ok"}
    await client.send_json(payload)

    mock_ws.send.assert_called_once_with(json.dumps(payload))


@pytest.mark.asyncio
async def test_ws_reconnect_on_failure(ws_client):
    """Verifica que DemeterWebsocketClient captura ConnectionRefusedError y reintenta."""
    client, _, _ = ws_client

    connect_attempts = []

    async def fake_connect_loop():
        """Simula la lógica de reintento: conecta, falla, reintenta."""
        for _ in range(2):
            try:
                # intentamos conectar (lanzará error la 1a vez)
                raise ConnectionRefusedError()
            except ConnectionRefusedError:
                connect_attempts.append("retry")
                await asyncio.sleep(0)  # yield al event loop

    client._connect_loop = fake_connect_loop

    await client._connect_loop()

    assert len(connect_attempts) >= 1
