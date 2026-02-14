import asyncio
import json
import logging
import os
import sys

# Add src to path to ensure imports work
# Add project root to path to ensure imports work (allows importing 'tests' and 'src')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

try:
    from proyecto_demeter.server.transport.async_uart import AsyncUartTransport
    from proyecto_demeter.shared.config.schemas import (
        GpioCommand, ActionResponse, PingCommand, SequenceCommand, ExecSequence, 
        GetSensorsCommand, TempHumReport, PinReport, SystemReport, Ack, Nack, CmdId,
        SetGpio, Ping, GetSensors, Syn
    )
    from proyecto_demeter.shared.protocols.protocol_v2 import DemeterProtocolV2
    from proyecto_demeter.server.data.database import DatabaseManager
    from proyecto_demeter.server.data.file_logger import SensorLogger
    from proyecto_demeter.shared.config.provider import settings
    # MockTransport Removed per user request
    pass
except ImportError as e:
    # re-raise to debug path issues instead of silently switching class loaders
    logging.error(f"Import Error in async_service: {e}")
    raise
    
from pydantic import ValidationError

# Configuration
# Use settings from provider.py for consistency
UART_PORT = settings.PORT
UART_BAUD = 115200
SOCKET_HOST = settings.HOST
SOCKET_PORT = settings.SOCKET_PORT

class DemeterService:
    def __init__(self):
        handlers = [logging.StreamHandler(sys.stdout)]
        if settings.LOG_FILE_PATH:
             # Ensure dir exists
             os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
             handlers.append(logging.FileHandler(settings.LOG_FILE_PATH))

        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger("DemeterService")
        
        self.transport = None
        self.protocol = DemeterProtocolV2()
        self.clients = set() # Set of TCP writers
        self.server = None
        
        # Buffer for incoming UART bytes
        self.rx_buffer = bytearray()

        # Data Layer
        self.data_manager = DatabaseManager()
        self.sensor_logger = SensorLogger()

    async def start(self):
        """Start all async tasks."""
        self.logger.info("[START] Starting Demeter Async Service...")
        
        # Init DB
        await self.data_manager.init_db()
        
        # 1. Start TCP Server (IPC)
        # reuse_address=True and reuse_port=True (on supported OS) helps avoid "Address already in use"
        # during rapid restarts.
        self.server = await asyncio.start_server(
            self.handle_tcp_client, 
            SOCKET_HOST, 
            SOCKET_PORT,
            reuse_address=True,
            reuse_port=hasattr(os, "SO_REUSEPORT")
        )
        addr = self.server.sockets[0].getsockname()
        self.logger.info(f"[NET] TCP Server listening on {addr}")

        # 2. Start Transport (Hardware Only)
        # Init transport with callback
        self.transport = AsyncUartTransport(UART_PORT, UART_BAUD)
        self.transport.set_callback(self.on_uart_data)
        
        if await self.transport.connect():
            self.logger.info(f"[HW] UART Connected to {UART_PORT}")
        else:
            self.logger.error("[ERR] UART Connect Failed")
            # Fail hard if we can't connect, as requested (no mocks)
            # We can run without transport (listeners only) or exit.
            # For now, just log error. Protocol commands will fail gracefully (check for self.transport).

        # 3. Handshake Initiation (Active Repeater Discovery)
        # We initiate handshake with known nodes to ensure routes are established
        # and to verify they are online.
        if self.transport:
             known_nodes = [2, 3] # TODO: Load from devices.json or config
             self.logger.info(f"[INIT] Initiating Handshake with Nodes {known_nodes}...")
             for node_id in known_nodes:
                 # Send SYN (Context 0 or Session Start)
                 sys_syn = self.protocol.serialize(Syn(target_id=node_id, context=0))
                 await self.transport.send(sys_syn)
                 # We don't wait for ACK here, handled in on_uart_data callback
                 await asyncio.sleep(0.1) # Brief pause

        # 4. Keep alive
        async with self.server:
            await self.server.serve_forever()

    def on_uart_data(self, data: bytes):
        """Callback for UART RX. Appends to buffer and processes frames."""
        try:
            # self.logger.debug(f"[RX] UART Chunk: {data.hex()}")
            self.rx_buffer.extend(data)
            self.process_buffer()
        except Exception as e:
            self.logger.error(f"RX Handler Error: {e}")

    def process_buffer(self):
        """
        Scans buffer for valid frames.
        Structure: [SYNC(0xFE)] [LEN] ... payload ... [CRC]
        """
        while len(self.rx_buffer) > 0:
            # 1. Find SYNC Byte
            try:
                sync_index = self.rx_buffer.index(0xFE)
            except ValueError:
                # No sync byte found, discard entire buffer (garbage)
                self.rx_buffer.clear()
                return

            # Discard garbage before SYNC
            if sync_index > 0:
                self.logger.warning(f"Discarding {sync_index} garbage bytes")
                del self.rx_buffer[:sync_index]

            # Now buffer starts with 0xFE
            if len(self.rx_buffer) < 2:
                # Not enough data for Length byte
                return

            # Get Payload Length
            payload_len = self.rx_buffer[1]
            # Total Frame Size = Header(6) + Payload(len) + CRC(1)
            # Header size is 6 bytes (SYNC, LEN, FLAGS, SRC, DST, CMD)
            total_frame_len = 6 + payload_len + 1

            if len(self.rx_buffer) < total_frame_len:
                # Incomplete frame, wait for more data
                return

            # Extract full frame
            frame = self.rx_buffer[:total_frame_len]
            
            # Remove frame from buffer
            del self.rx_buffer[:total_frame_len]
            
            # 2. Parse Frame
            cmd = self.protocol.parse_frame(bytes(frame))
            if cmd:
                # Schedule async handler
                asyncio.create_task(self.handle_protocol_command(cmd))
            else:
                self.logger.warning(f"Invalid Frame (CRC or Structure): {frame.hex()}")

    async def handle_protocol_command(self, cmd):
        """Dispatch received protocol commands."""
        # self.logger.info(f"RX Parsed: {cmd}")
        
        # Broadcast DataReports to all connected GUI clients
        if isinstance(cmd, TempHumReport): # DataReport replacement
            self.logger.info(f"[RX] TempHum Node={cmd.node_id} Temp={cmd.temperature:.1f} Hum={cmd.humidity:.1f}")
            
            # Log & Save
            self.sensor_logger.log_reading(cmd.node_id, cmd.temperature, cmd.humidity)
            await self.data_manager.save_reading(cmd.node_id, cmd.temperature, cmd.humidity)

            self.broadcast_event(cmd)
            
        elif isinstance(cmd, PinReport):
            self.logger.info(f"[RX] PinReport Node={cmd.node_id} Pin={cmd.pin} State={cmd.state}")
            self.broadcast_event(cmd)

        elif isinstance(cmd, SystemReport):
            self.logger.info(f"[RX] SystemReport Node={cmd.node_id} Mode={cmd.mode} Batt={cmd.battery_mv}mV")
            self.broadcast_event(cmd)
            
        elif isinstance(cmd, Ack):
            self.logger.info(f"[ACK] Device ACK for CMD {cmd.original_cmd_id}")
            # Could forward ACK to GUI if we mapped request IDs
            
        elif isinstance(cmd, Nack):
            self.logger.warning(f"[NACK] Device NACK for CMD {cmd.original_cmd_id} (Err: {cmd.error_code})")

    def broadcast_event(self, model):
        """Send a Pydantic model as JSON to all TCP clients."""
        try:
            json_str = model.model_dump_json()
            # We might want to wrap it in a structure {"type": "EVENT", "payload": ...}
            # But for simplicity, if it's a DataReport, clients can check 'type' or fields.
            # DataReport has fields 'node_id', 'temperature', 'humidity'.
            # Let's wrap to be safe/consistent?
            # Or just send it. Let's send raw JSON of the model.
            data = json_str.encode() + b'\n'
            
            # Iterate copy of set to handle disconnection during iteration safely
            for writer in list(self.clients):
                try:
                    writer.write(data)
                    # We can't await drain() easily in a sync callback (on_uart_data -> process_buffer -> handle).
                    # So we just write. asyncio transport will buffer.
                    # Ideally we should use loop.create_task(writer.drain()) or similar if we care about backpressure.
                except Exception as e:
                    self.logger.error(f"Broadcast error: {e}")
                    self.clients.discard(writer)
                    
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")

    async def handle_tcp_client(self, reader, writer):
        """Handle incoming TCP connections from TUI/GUI."""
        addr = writer.get_extra_info('peername')
        self.logger.info(f"[NET] New Client: {addr}")
        self.clients.add(writer)

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                
                message = data.decode().strip()
                self.logger.debug(f"[{addr}] RX: {message}")
                
                # --- Pydantic Processing ---
                try:
                    msg_json = json.loads(message)
                    cmd_type = msg_json.get("type")
                    
                    response_obj = None

                    if cmd_type == "GPIO_CMD":
                        cmd = GpioCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] GPIO Command: PIN={cmd.pin} ACT={cmd.action} TARGET={cmd.target_id}")
                         # Execute (Mock or Real)
                        if not self.transport:
                            response_obj = ActionResponse(status="ERROR", message="No Transport Available")
                        else:
                            response_obj = await self._execute_real_gpio(cmd)

                    elif cmd_type == "PING_CMD":
                        cmd = PingCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] PING Command: Target={cmd.target_id}")
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                            await self._send_protocol_cmd(self.protocol.serialize(Ping(target_id=cmd.target_id)))
                            response_obj = ActionResponse(status="OK", message="Ping Sent")

                    elif cmd_type == "GET_SENSORS_CMD":
                        cmd = GetSensorsCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] GET_SENSORS: Target={cmd.target_id}")
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                             await self._send_protocol_cmd(self.protocol.serialize(GetSensors(target_id=cmd.target_id)))
                             response_obj = ActionResponse(status="OK", message="Data Request Sent")

                    elif cmd_type == "SEQ_CMD":
                        cmd = SequenceCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] SEQUENCE Command: {len(cmd.steps)} steps")
                        
                        exec_seq = ExecSequence(target_id=cmd.target_id, steps=cmd.steps)
                        
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                             # Serialize manually since helper might not exist for Sequence
                             bytes_seq = self.protocol.serialize(exec_seq)
                             await self._send_protocol_cmd(bytes_seq)
                             response_obj = ActionResponse(status="OK", message="Sequence Sent")

                    else:
                        # Check if it's a known schema that doesn't have "type" field like DataReport?
                        # No, commands from GUI should have structure.
                        self.logger.warning(f"Unknown Command Type: {cmd_type}")
                        response_obj = ActionResponse(status="ERROR", message="Unknown Command Type")

                    # 3. Send Response
                    if response_obj:
                        writer.write(response_obj.model_dump_json().encode() + b'\n')
                        await writer.drain()
                    
                except ValidationError as e:
                    self.logger.error(f"Validation Error: {e}")
                    err = ActionResponse(status="ERROR", message=f"Schema Error: {e}")
                    writer.write(err.model_dump_json().encode() + b'\n')
                    await writer.drain()
                except Exception as e:
                    self.logger.error(f"Processing Error: {e}")
                
        except Exception as e:
            self.logger.error(f"Client Error: {e}")
        finally:
            self.logger.info(f"[NET] Client Disconnected: {addr}")
            self.clients.remove(writer)
            try:
                writer.close()
            except: pass

    # _execute_mock_gpio REMOVED per user request

    async def _execute_real_gpio(self, cmd: GpioCommand) -> ActionResponse:
        """Send bytes to real hardware."""
        val = 1 if cmd.action == "ON" else 0
        if cmd.action == "TOGGLE":
            val = 2 # Let's assume 2 is Toggle for now, or just default to 1 if not supported
            # Actually Protocol V2 might need update for Toggle flag, but let's stick to 1/0
            if cmd.action == "TOGGLE":
                 # We can't toggle without knowing state in unidirectional protocol without query.
                 # Let's warn.
                 self.logger.warning("TOGGLE not fully supported in V2 statelessly. Sending ON.")
                 val = 1
        
        # Create Payload
        payload = self.protocol.serialize(SetGpio(target_id=cmd.target_id, pin=cmd.pin, value=val)) 
        await self._send_protocol_cmd(payload)
        
        return ActionResponse(status="OK", message="Command Sent to UART")

    async def _send_protocol_cmd(self, data: bytes):
        if self.transport:
            await self.transport.send(data)

if __name__ == "__main__":
    service = DemeterService()
    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        pass
