"""
command_dispatcher.py — GatewayOrchestrator

Bridges the WebSocket connection (server) and the UART bus (ESP32 nodes).

Message flow:
  Server  →  WS  →  dispatch_ws_to_uart()  →  UART  →  ESP32
  ESP32   →  UART → dispatch_uart_to_ws()  →  WS    →  Server

Outgoing WS messages use the exact `type` field expected by the server's
_handle_gateway_msg() in WS_Manager/dispatcher.py:
  - "temp_hum_report"
  - "pin_report"
  - "system_report"
  - "ack" / "nack"
"""

import asyncio
import logging
import json
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from demeter_protocol import DemeterProtocolV2
from schemas import (
    DemeterCommand, SetGpio, Ping, GetSensors, ExecSequence, SequenceStep,
    TempHumReport, PinReport, SystemReport, Ack, Nack, Syn, SynAck, CmdId,
)
from proyecto_demeter.Hardware.transport.uart_processor import UartProcessor
from proyecto_demeter.Hardware.ws_client.client import DemeterWebsocketClient
from proyecto_demeter.Hardware.management.device_manager import DeviceManager


# Tipos que llegan desde el UART (nodo) que se reenvían al servidor via WS.
# Los comandos de control interno (Ping, Syn, SynAck) se ignoran silenciosamente.
_REPORT_TYPE_MAP: Dict[type, str] = {
    TempHumReport: "temp_hum_report",
    PinReport:     "pin_report",
    SystemReport:  "system_report",
    Ack:           "ack",
    Nack:          "nack",
}


class GatewayOrchestrator:
    """
    Central Orchestrator bridging Protocol/UART and WebSocket/JSON.
    - Manages UartProcessor lifecycle.
    - Manages DemeterWebsocketClient lifecycle.
    - Routes messages: WS → UART and UART → WS.
    """

    def __init__(self):
        self.logger = logging.getLogger("GatewayOrchestrator")
        self.uart = UartProcessor()
        self.protocol = DemeterProtocolV2()
        self.device_manager = DeviceManager()
        self.ws_client = DemeterWebsocketClient(
        on_message_callback=self.dispatch_ws_to_uart,
        on_open_callback=self.report_system_config
    )

# ── Global App & Gateway Instance ──
app = FastAPI(title="Demeter Edge API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
gateway = GatewayOrchestrator()

# ── Edge API Routes ──
@app.post("/api/auth/login")
async def mock_login(request: Request):
    return {"access_token": "edge_local_token", "token_type": "bearer"}

@app.get("/api/devices")
async def get_devices():
    return {
        "status": "online",
        "devices": gateway.device_manager.get_config()
    }

@app.post("/api/command")
async def post_command(request: Request):
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return {"error": "Invalid JSON"}
    
    cmd_model = gateway._parse_incoming_command(data)
    if cmd_model:
        gateway.logger.info(f"[Edge API] Publishing local command: {type(cmd_model).__name__}")
        await gateway.uart.send_command(cmd_model)
        return {"status": "success"}
    return {"error": "Invalid command payload"}


# ── Lifecycle ─────────────────────────────────────────────────────────────

async def start_gateway():
    gateway.logger.info("Starting Gateway Orchestrator…")
    gateway.uart.add_listener(gateway.dispatch_uart_to_ws)
    uart_task = asyncio.create_task(gateway.uart.start())
    
    # Start Local API Server globally
    config = uvicorn.Config(app, host="0.0.0.0", port=8001, log_level="info")
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())

    await gateway.ws_client.start()
    await asyncio.gather(uart_task, api_task)

async def stop_gateway():
    await gateway.ws_client.stop()
    await gateway.uart.stop()


# ── WS → UART ─────────────────────────────────────────────────────────────

    @staticmethod
    def dispatch_ws_to_uart(raw_message: str) -> None:
        """
        Recibe un comando JSON desde el servidor WebSocket y lo reenvía por UART.

        El servidor (o frontend) debe enviar JSON con el campo `type`:
            {"type": "set_gpio",      "target_id": 1, "pin": 4, "value": 1}
            {"type": "exec_sequence", "target_id": 1, "steps": [...]}
            {"type": "ping",          "target_id": 1}

        Pydantic discrimina el tipo automáticamente. No hay lógica if/elif.
        """
        try:
            data: Dict[str, Any] = json.loads(raw_message)
        except json.JSONDecodeError:
            print("dispatch_ws_to_uart: JSON inválido recibido")
            return

        print(f"[WS RX] {data}")

        cmd_model = gateway._parse_incoming_command(data)
        if cmd_model:
            print(f"[Bridge WS→UART] Enviando {type(cmd_model).__name__} por UART")
            asyncio.create_task(gateway.uart.send_command(cmd_model))
        else:
            print(f"[Bridge WS→UART] No se pudo mapear el comando: {data}")


    def _parse_incoming_command(self, data: Dict[str, Any]) -> Optional[DemeterCommand]:
        """
        Convierte un dict JSON en el DemeterCommand tipado correspondiente.
        Aplica traducción de hardware via DeviceManager si es necesario.
        """
        # ── Hardware Translation ──
        cmd_type = data.get("type")
        
        if cmd_type == "set_gpio":
            logical_pin = data.get("pin")
            if isinstance(logical_pin, int):
                target_id, physical_pin = self.device_manager.translate_pin(logical_pin)
                self.logger.debug(f"Translating pin {logical_pin} -> Node {target_id}, Pin {physical_pin}")
                data["target_id"] = target_id
                data["pin"] = physical_pin
                
        elif cmd_type == "exec_sequence":
            for step in data.get("steps", []):
                logical_pin = step.get("pin")
                if isinstance(logical_pin, int) and logical_pin != 0: # 0 is WAIT
                    target_id, physical_pin = self.device_manager.translate_pin(logical_pin)
                    step["target_id"] = target_id
                    step["pin"] = physical_pin

        # ── Parsing ──
        try:
            return self.protocol.validate_json_message(data)
        except Exception as exc:
            self.logger.warning(f"_parse_incoming_command: {exc} | data={data}")
            return None

    async def report_system_config(self) -> None:
        """
        Sends the local hardware configuration to the server.
        Triggered automatically on WebSocket connect.
        """
        config = self.device_manager.get_config()
        payload = {
            "type": "system_config",
            "devices": config
        }
        self.logger.info("Reporting system configuration to backend...")
        await self.ws_client.send_json(payload)

    # ── UART → WS ─────────────────────────────────────────────────────────────

    async def dispatch_uart_to_ws(self, cmd: DemeterCommand) -> None:
        """
        Receive a parsed command from the UART bus and publish it to the server
        WebSocket using the type string that the server's _handle_gateway_msg()
        expects (e.g. "temp_hum_report", "pin_report", "ack", "nack").
        """
        msg_type = _REPORT_TYPE_MAP.get(type(cmd))
        if msg_type is None:
            # Silently ignore protocol-internal commands (Ping, Syn, SynAck…)
            return

        payload = {
            "type": msg_type,
            **cmd.model_dump(),   # flatten all fields at the top level
        }

        self.logger.debug(f"[Bridge UART→WS] {msg_type}: {payload}")
        await self.ws_client.send_json(payload)


if __name__ == "__main__":
    orchestrator = GatewayOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        pass
