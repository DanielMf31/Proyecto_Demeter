import asyncio
import json
import logging
import os
import sys

# Add src to path to ensure imports work
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

try:
    from proyecto_demeter.transport.async_uart import AsyncUartTransport
    from proyecto_demeter.shared.schemas import GpioCommand, ActionResponse, PingCommand, SequenceCommand, ExecSequence, GetSensorsCommand
    from proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
except ImportError:
    # Fallback for direct execution
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    from src.proyecto_demeter.transport.async_uart import AsyncUartTransport
    from src.proyecto_demeter.transport.async_uart import AsyncUartTransport
    from src.proyecto_demeter.shared.schemas import GpioCommand, ActionResponse,  PingCommand, SequenceCommand, ExecSequence
    from src.proyecto_demeter.protocols.protocol_v2 import DemeterProtocolV2
    
from pydantic import ValidationError

# Configuration
UART_PORT = os.getenv('DEMETER_PORT', '/dev/serial0')
UART_BAUD = 115200
SOCKET_HOST = os.getenv('DEMETER_HOST', '0.0.0.0') # Listen on all interfaces by default
SOCKET_PORT = int(os.getenv('DEMETER_SOCKET_PORT', 8888))
MOCK_MODE = os.getenv('DEMETER_MOCK', 'False').lower() == 'true'

class DemeterService:
    def __init__(self):
        handlers = [logging.StreamHandler(sys.stdout)]
        log_file = os.environ.get("DEMETER_LOG_FILE")
        if log_file:
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger("DemeterService")
        
        self.transport = None
        self.protocol = DemeterProtocolV2()
        self.clients = set() # Set of TCP writers
        self.server = None
        self.mock_gpio_state = {} # For Mock Mode
        
        # Buffer for incoming UART bytes
        self.rx_buffer = bytearray()

    async def start(self):
        """Start all async tasks."""
        self.logger.info("[START] Starting Demeter Async Service...")
        
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

        # 2. Start UART Transport (Hardware)
        if MOCK_MODE:
            self.logger.warning("[WARN] RUNNING IN MOCK MODE (No Hardware connection)")
        else:
            # Init transport with callback
            self.transport = AsyncUartTransport(UART_PORT, UART_BAUD)
            self.transport.set_callback(self.on_uart_data)
            
            try:
                if await self.transport.connect():
                    self.logger.info(f"[HW] UART Connected to {UART_PORT}")
                else:
                    self.logger.error("[ERR] UART Connect Failed")
                    self.logger.warning("   -> Switching to MOCK behavior for stability.")
            except Exception as e:
                self.logger.error(f"[ERR] UART Connection Exception: {e}")
                self.logger.warning("   -> Switching to MOCK behavior for stability.")

        # 3. Keep alive
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
                self.handle_protocol_command(cmd)
            else:
                self.logger.warning(f"Invalid Frame (CRC or Structure): {frame.hex()}")

    def handle_protocol_command(self, cmd):
        """Dispatch received protocol commands."""
        # self.logger.info(f"RX Parsed: {cmd}")
        
        # Broadcast DataReports to all connected GUI clients
        if cmd.get_cmd_id() == 0x0B: # DataReport
            self.logger.info(f"[RX] DataReport Node={cmd.node_id} Temp={cmd.temperature:.1f} Hum={cmd.humidity:.1f}")
            self.broadcast_event(cmd)
            
        elif cmd.get_cmd_id() == 0xF0: # ACK
            self.logger.info(f"[ACK] Device ACK for CMD {cmd.original_cmd_id}")
            # Could forward ACK to GUI if we mapped request IDs
            
        elif cmd.get_cmd_id() == 0xF1: # NACK
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
            data = json_str.encode()
            
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
                        self.logger.info(f"[CMD] GPIO Command: PIN={cmd.pin} ACT={cmd.action}")
                         # Execute (Mock or Real)
                        if MOCK_MODE or not self.transport:
                            response_obj = self._execute_mock_gpio(cmd)
                        else:
                            response_obj = await self._execute_real_gpio(cmd)

                    elif cmd_type == "PING_CMD":
                        cmd = PingCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] PING Command: Target={cmd.target_id}")
                        if MOCK_MODE or not self.transport:
                             response_obj = ActionResponse(status="OK", message=f"MOCK: Pong from {cmd.target_id}")
                        else:
                            await self._send_protocol_cmd(self.protocol.create_ping(cmd.target_id))
                            response_obj = ActionResponse(status="OK", message="Ping Sent")

                    elif cmd_type == "GET_SENSORS_CMD":
                        cmd = GetSensorsCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] GET_SENSORS: Target={cmd.target_id}")
                        if MOCK_MODE or not self.transport:
                             response_obj = ActionResponse(status="OK", message="MOCK: Data Requested")
                        else:
                             await self._send_protocol_cmd(self.protocol.create_get_sensors(cmd.target_id))
                             response_obj = ActionResponse(status="OK", message="Data Request Sent")

                    elif cmd_type == "SEQ_CMD":
                        cmd = SequenceCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] SEQUENCE Command: {len(cmd.steps)} steps")
                        
                        exec_seq = ExecSequence(target_id=cmd.target_id, steps=cmd.steps)
                        
                        if MOCK_MODE or not self.transport:
                             response_obj = ActionResponse(status="OK", message="MOCK: Sequence Started")
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
                        writer.write(response_obj.model_dump_json().encode())
                        await writer.drain()
                    
                except ValidationError as e:
                    self.logger.error(f"Validation Error: {e}")
                    err = ActionResponse(status="ERROR", message=f"Schema Error: {e}")
                    writer.write(err.model_dump_json().encode())
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

    def _execute_mock_gpio(self, cmd: GpioCommand) -> ActionResponse:
        """Simulate hardware action."""
        current = self.mock_gpio_state.get(cmd.pin, False)
        
        if cmd.action == "ON":
            new_state = True
        elif cmd.action == "OFF":
            new_state = False
        else: # TOGGLE
            new_state = not current
            
        self.mock_gpio_state[cmd.pin] = new_state
        self.logger.info(f"💡 [MOCK] Pin {cmd.pin} -> {new_state}")
        
        return ActionResponse(
            status="OK",
            message=f"MOCK: Pin {cmd.pin} set to {cmd.action}",
            pin_state=new_state
        )

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
        payload = self.protocol.create_set_gpio(target_id=1, pin=cmd.pin, value=val) # Target 1 (Gateway) usually
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
