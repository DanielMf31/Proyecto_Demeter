import asyncio
import pytest
import subprocess
import time
import socket
import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from proyecto_demeter.config.schemas import GpioCommand, ActionResponse

SERVICE_SCRIPT = os.path.join(os.path.dirname(__file__), '../src/proyecto_demeter/core/async_service.py')
PYTHON_EXE = sys.executable

@pytest.fixture(scope="module")
def async_service():
    """Start the Async Service in Mock Mode."""
    env = os.environ.copy()
    env["DEMETER_MOCK"] = "True"
    
    print("🚀 Starting Mock Service...")
    proc = subprocess.Popen(
        [PYTHON_EXE, SERVICE_SCRIPT],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2) # Wait for startup
    yield proc
    print("🛑 Killing Service...")
    proc.terminate()
    proc.wait()

@pytest.mark.asyncio
async def test_gpio_command_flow(async_service):
    """Test that valid JSON commands receive valid JSON responses."""
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    
    # 1. Create Command
    cmd = GpioCommand(pin=2, action="ON")
    writer.write(cmd.model_dump_json().encode())
    await writer.drain()
    
    # 2. Read Response
    data = await reader.read(1024)
    response_json = data.decode()
    
    # 3. Validate Response
    resp = ActionResponse.model_validate_json(response_json)
    assert resp.status == "OK"
    assert resp.pin_state is True
    assert "MOCK" in resp.message
    
    print("\n✅ Test Passed: GPIO ON Command -> OK Response")
    writer.close()
    await writer.wait_closed()
