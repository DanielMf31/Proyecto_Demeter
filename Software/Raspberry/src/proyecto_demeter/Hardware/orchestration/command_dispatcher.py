import asyncio
import logging
import json
from typing import Dict, Any, Optional

from demeter_protocol import DemeterProtocolV2
from schemas import (
    DemeterCommand, SetGpio, Ping, GetSensors, ExecSequence, SequenceCommand, SequenceStep,
    TempHumReport, PinReport, SystemReport, Ack, Nack, Syn, SynAck
)
from proyecto_demeter.Hardware.transport.uart_processor import UartProcessor
from proyecto_demeter.Hardware.ws_client.client import DemeterWebsocketClient
from configuration import settings

class GatewayOrchestrator:
    """
    Central Orchestrator bridging Protocol/UART and WebSocket/JSON.
    - Manages UartProcessor lifecycle.
    - Manages DemeterWebsocketClient lifecycle.
    - Routes messages: WS -> UART and UART -> WS.
    """
    def __init__(self):
        # Components
        self.logger = logging.getLogger("GatewayOrchestrator")
        self.uart = UartProcessor()
        self.protocol = DemeterProtocolV2()
        
        # Instantiate WS Client with callback
        self.ws_client = DemeterWebsocketClient(self.dispatch_ws_to_uart)

    async def start(self):
        """Start all services."""
        self.logger.info("Starting Gateway Orchestrator...")

        # 1. Wire up UART Listener (Traffic from Nodes -> WS)
        self.uart.add_listener(self.dispatch_uart_to_ws)

        # 2. Start Services
        uart_task = asyncio.create_task(self.uart.start())
        await self.ws_client.start()

        # Wait for UART (which runs forever)
        await uart_task

    async def stop(self):
        await self.ws_client.stop()
        await self.uart.stop()

    # =========================================================================
    # Routing Logic
    # =========================================================================

    async def dispatch_ws_to_uart(self, raw_message: str):
        """
        Received JSON from WebSocket -> Send Valid Command via UART.
        """
        try:
            data = json.loads(raw_message)
            self.logger.debug(f"[WS RX] {data}")
            
            # 1. Parse JSON to Pydantic Model
            cmd_model: Optional[DemeterCommand] = self._parse_json_command(data)

            if cmd_model:
                self.logger.info(f"[Bridge] Forwarding {cmd_model} to UART")
                await self.uart.send_command(cmd_model)
            else:
                self.logger.warning(f"[Bridge] Could not map JSON to Command: {data}")

        except json.JSONDecodeError:
            self.logger.error("Invalid JSON received from WS")
        except Exception as e:
            self.logger.error(f"Dispatch WS->UART Error: {e}")

    async def dispatch_uart_to_ws(self, cmd: DemeterCommand):
        """
        Received Command from UART -> Publish JSON to WebSocket.
        """
        # Filter: Only forward reports or specific events, not every ACK?
        
        if isinstance(cmd, (TempHumReport, PinReport, SystemReport, Nack, Ack)):
            try:
                # Create standard JSON payload
                payload = {
                    "type": "telemetry", # or event
                    "source": "uart",
                    "node_id": cmd.source_id,
                    "data": cmd.model_dump()
                }
                
                await self.ws_client.send_json(payload)
                self.logger.debug(f"[Bridge] Forwarded UART->WS: {payload}")
            except Exception as e:
                self.logger.error(f"Dispatch UART->WS Error: {e}")

    # =========================================================================
    # Helpers
    # =========================================================================
    def _parse_json_command(self, data: Dict[str, Any]) -> Optional[DemeterCommand]:
        """Convert Dictionary to DemeterCommand using Strict Protocol."""
        try:
            return self.protocol.validate_json_message(data)
        except ValueError as e:
            self.logger.warning(f"Protocol Validation Failed: {e}")
            return None


if __name__ == "__main__":
    # Standalone Entry Point
    orchestrator = GatewayOrchestrator()
    try:
        asyncio.run(orchestrator.start())
    except KeyboardInterrupt:
        pass
