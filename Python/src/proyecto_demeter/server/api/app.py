from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import logging
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from proyecto_demeter.server.core.async_service import DemeterService
from proyecto_demeter.shared.config.schemas import GpioCommand, SequenceCommand, ActionResponse
from proyecto_demeter.shared.config.provider import settings

app = FastAPI(title="Demeter Core API", version="2.0.0")
service = DemeterService()

@app.on_event("startup")
async def startup_event():
    # Run the service start in a separate task so it doesn't block FastAPI
    asyncio.create_task(service.start())

@app.post("/command/gpio", response_model=ActionResponse)
async def send_gpio_command(cmd: GpioCommand):
    if not service.transport:
        raise HTTPException(status_code=503, detail="Hardware transport not available")
    
    try:
        response = await service._execute_real_gpio(cmd)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/command/sequence", response_model=ActionResponse)
async def send_sequence_command(cmd: SequenceCommand):
    if not service.transport:
        raise HTTPException(status_code=503, detail="Hardware transport not available")
    
    try:
        from proyecto_demeter.shared.config.schemas import ExecSequence
        exec_seq = ExecSequence(target_id=cmd.target_id, steps=cmd.steps)
        bytes_seq = service.protocol.serialize(exec_seq)
        await service._send_protocol_cmd(bytes_seq)
        return ActionResponse(status="OK", message="Sequence Sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    return {
        "status": "online",
        "transport_connected": service.transport is not None and service.transport.writer is not None,
        "clients_connected": len(service.clients)
    }
