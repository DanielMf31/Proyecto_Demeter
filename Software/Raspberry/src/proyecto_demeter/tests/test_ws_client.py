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
        # Run only one iteration of the loop by setting running to False after it starts
        task = asyncio.create_task(client._connect_loop())
        
        # Wait for calls
        for _ in range(50):
            if on_msg.call_count >= 1: break
            await asyncio.sleep(0.01)
        
        client.running = False
        assert mock_websockets.connect.call_count >= 1
        on_open.assert_called_once()
        on_msg.assert_called_with("{\"type\": \"ping\"}")
        
        task.cancel()
        try: await asyncio.wait_for(task, timeout=0.1)
        except (asyncio.CancelledError, asyncio.TimeoutError): pass

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
    client, _, _ = ws_client
    client.running = True
    
    mock_ok = AsyncMock()
    mock_ok.__aiter__.return_value = []
    
    cm_ok = AsyncMock()
    cm_ok.__aenter__.return_value = mock_ok
    
    with patch('proyecto_demeter.Hardware.ws_client.client.websockets') as mock_websockets, \
         patch('proyecto_demeter.Hardware.ws_client.client.asyncio.sleep', AsyncMock()) as mock_sleep:
        
        mock_websockets.connect.side_effect = [ConnectionRefusedError(), cm_ok]
        
        task = asyncio.create_task(client._connect_loop())
        
        # We need to yield to the loop so the task can run
        for _ in range(100):
            await asyncio.sleep(0) # Yield many times to let AsyncMock sleep return immediately
            if mock_websockets.connect.call_count >= 2: break
            
        client.running = False
        assert mock_websockets.connect.call_count >= 2
        task.cancel()
        try: await asyncio.wait_for(task, timeout=0.1)
        except (asyncio.CancelledError, asyncio.TimeoutError): pass
