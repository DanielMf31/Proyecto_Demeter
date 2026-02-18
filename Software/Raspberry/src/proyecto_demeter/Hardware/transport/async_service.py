import asyncio
import json
import logging
import os
import sys

# Add project root and Common to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Path: .../Software/Raspberry/src/proyecto_demeter/Hardware/transport
# We need .../Software/Common
# Go up: transport(1) -> Hardware(2) -> demeter(3) -> src(4) -> Raspberry(5) -> Software(6)
SOFTWARE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../../../../../../'))
COMMON_DIR = os.path.join(SOFTWARE_DIR, 'Common')

if COMMON_DIR not in sys.path:
    sys.path.append(COMMON_DIR)
# Also add project root (Raspberry) to path for local imports if needed
RASPBERRY_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '../../../../../'))
if RASPBERRY_DIR not in sys.path:
     sys.path.append(RASPBERRY_DIR)

try:
    from proyecto_demeter.Hardware.transport.uart_processor import UartProcessor
    from proyecto_demeter.Hardware.ws_client.client import DemeterWebsocketClient
    from demeter_protocol import DemeterProtocolV2
    from schemas import (
        DemeterCommand, GpioCommand, ActionResponse, PingCommand, SequenceCommand, ExecSequence, 
        GetSensorsCommand, TempHumReport, PinReport, SystemReport, Ack, Nack, CmdId,
        SetGpio, Ping, GetSensors, Syn, SynAck
    )
    from proyecto_demeter.utils.database import DatabaseManager
    # from proyecto_demeter.server.data.file_logger import SensorLogger # Disabling old logger for now or map it
    from configuration import settings

except ImportError as e:
    logging.error(f"Import Error in Uart_processor: {e}")
    logging.error(f"Sys Path: {sys.path}")
    raise
    
from pydantic import ValidationError

UART_PORT = settings.PORT
UART_BAUD = settings.UART_BAUD
SOCKET_HOST = settings.HOST
SOCKET_PORT = settings.SOCKET_PORT

class DemeterService:
    def __init__(self):
        handlers = [logging.StreamHandler(sys.stdout)]
        if settings.LOG_FILE_PATH:
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
        self.clients = set()
        self.server = None
        
        # RX Architecture
        self.rx_buffer = bytearray()
        self.rx_queue = asyncio.Queue()
        
        self.data_manager = DatabaseManager()
        self.sensor_logger = SensorLogger()

    async def start(self):
        """Start all async tasks."""
        self.logger.info("[START] Starting Demeter Async Service...")
        
        await self.data_manager.init_db()
        
        # 1. Start TCP Server
        self.server = await asyncio.start_server(
            self.handle_tcp_client, 
            SOCKET_HOST, 
            SOCKET_PORT,
            reuse_address=True,
            reuse_port=hasattr(os, "SO_REUSEPORT")
        )
        addr = self.server.sockets[0].getsockname()
        self.logger.info(f"[NET] TCP Server listening on {addr}")

        # 2. Start Transport (UART)
        self.transport = AsyncUartTransport(UART_PORT, UART_BAUD)
        self.transport.set_callback(self.on_uart_data)
        
        if await self.transport.connect():
            self.logger.info(f"[HW] UART Connected to {UART_PORT}")
        else:
            self.logger.error("[ERR] UART Connect Failed")

        # 3. Start Dispatcher (Consumer)
        asyncio.create_task(self._dispatch_loop())

        # 4. Handshake
        if self.transport:
             known_nodes = [2, 3] # TODO: Load from config
             self.logger.info(f"[INIT] Initiating Handshake with Nodes {known_nodes}...")
             for node_id in known_nodes:
                 sys_syn = self.protocol.pack_frame(Syn(target_id=node_id, context=0))
                 await self.transport.send(sys_syn)
                 await asyncio.sleep(0.1)

        # 5. Serve
        async with self.server:
            await self.server.serve_forever()

    def on_uart_data(self, data: bytes):
        """Callback for UART RX (Producer)."""
        try:
            self.rx_buffer.extend(data)
            self.process_buffer()
        except Exception as e:
            self.logger.error(f"RX Handler Error: {e}")

    def process_buffer(self):
        """Scans buffer for valid frames using ProtocolV2 logic."""
        SYNC = 0xFE
        
        while True:
            try:
                sync_index = self.rx_buffer.index(SYNC)
            except ValueError:
                self.rx_buffer.clear()
                return

            if sync_index > 0:
                del self.rx_buffer[:sync_index]

            if len(self.rx_buffer) < 2:
                return

            payload_len = self.rx_buffer[1]
            total_frame_len = 6 + payload_len + 1 # Header(6) + Payload + CRC(1)

            if len(self.rx_buffer) < total_frame_len:
                return

            frame_bytes = bytes(self.rx_buffer[:total_frame_len])
            cmd = self.protocol.parse_frame(frame_bytes)
            
            if cmd:
                del self.rx_buffer[:total_frame_len]
                # Put valid command into Queue
                try:
                    self.rx_queue.put_nowait(cmd)
                except Exception as e:
                    self.logger.error(f"Queue Full/Error: {e}")
            else:
                self.logger.warning(f"Invalid Frame. Dropping SYNC. Data: {frame_bytes.hex()}")
                del self.rx_buffer[0]

    async def _dispatch_loop(self):
        """Consumer Task: Reads from rx_queue and executes logic."""
        self.logger.info("[CORE] Starting Dispatch Loop")
        while True:
            try:
                cmd = await self.rx_queue.get()
                await self.handle_protocol_command(cmd)
                self.rx_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Dispatch Error: {e}")

    async def handle_protocol_command(self, cmd: DemeterCommand):
        """Business Logic for received commands."""
        
        if isinstance(cmd, TempHumReport):
            self.logger.info(f"[RX] TempHum Node={cmd.node_id} Temp={cmd.temperature:.1f} Hum={cmd.humidity:.1f}")
            self.sensor_logger.log_reading(cmd.node_id, cmd.temperature, cmd.humidity)
            await self.data_manager.save_reading(cmd.node_id, cmd.temperature, cmd.humidity)
            self.broadcast_event(cmd)
            
        elif isinstance(cmd, PinReport):
            self.logger.info(f"[RX] PinReport Node={cmd.node_id} Pin={cmd.pin} State={cmd.state}")
            self.broadcast_event(cmd)

        elif isinstance(cmd, SystemReport):
            self.logger.info(f"[RX] SystemReport Node={cmd.node_id} Mode={cmd.mode} Batt={cmd.battery_mv}mV")
            self.broadcast_event(cmd)
            
        elif isinstance(cmd, Syn):
            self.logger.info(f"[SYN] Handshake Request from Node {cmd.source_id}")
            if cmd.source_id is not None:
                reply = self.protocol.pack_frame(SynAck(target_id=cmd.source_id, context=cmd.context))
                await self._send_protocol_cmd(reply)

        elif isinstance(cmd, Ack):
            self.logger.info(f"[ACK] Device ACK for CMD {cmd.original_cmd_id}")
            
        elif isinstance(cmd, Nack):
            self.logger.warning(f"[NACK] Device NACK for CMD {cmd.original_cmd_id} (Err: {cmd.error_code})")

    def broadcast_event(self, model: DemeterCommand):
        """Send Pydantic model as JSON to TCP clients."""
        try:
            json_str = model.model_dump_json() + '\n'
            data = json_str.encode()
            for writer in list(self.clients):
                try:
                    writer.write(data)
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
                if not data: break
                
                message = data.decode().strip()
                self.logger.debug(f"[{addr}] RX: {message}")
                
                try:
                    msg_json = json.loads(message)
                    cmd_type = msg_json.get("type")
                    
                    response_obj = None

                    # DIRECT MAPPING (Relaxed Validation)
                    if cmd_type == "GPIO_CMD":
                        cmd = GpioCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] GPIO Command: PIN={cmd.pin} ACT={cmd.action} TARGET={cmd.target_id}")
                        if not self.transport:
                            response_obj = ActionResponse(status="ERROR", message="No Transport Available")
                        else:
                            val = 1 if cmd.action == "ON" else 0 
                            # Toggle logic check kept simple
                            frame = self.protocol.pack_frame(SetGpio(target_id=cmd.target_id, pin=cmd.pin, value=val)) 
                            await self._send_protocol_cmd(frame)
                            response_obj = ActionResponse(status="OK", message="Command Sent")

                    elif cmd_type == "PING_CMD":
                        cmd = PingCommand.model_validate(msg_json)
                        self.logger.info(f"[CMD] PING Command: Target={cmd.target_id}")
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                            await self._send_protocol_cmd(self.protocol.pack_frame(Ping(target_id=cmd.target_id)))
                            response_obj = ActionResponse(status="OK", message="Ping Sent")

                    elif cmd_type == "GET_SENSORS_CMD":
                        cmd = GetSensorsCommand.model_validate(msg_json)
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                             await self._send_protocol_cmd(self.protocol.pack_frame(GetSensors(target_id=cmd.target_id)))
                             response_obj = ActionResponse(status="OK", message="Request Sent")

                    elif cmd_type == "SEQ_CMD":
                        cmd = SequenceCommand.model_validate(msg_json)
                        exec_seq = ExecSequence(target_id=cmd.target_id, steps=cmd.steps)
                        if not self.transport:
                             response_obj = ActionResponse(status="ERROR", message="No Transport")
                        else:
                             await self._send_protocol_cmd(self.protocol.pack_frame(exec_seq))
                             response_obj = ActionResponse(status="OK", message="Sequence Sent")

                    # Allow generic "command" passing if needed (e.g. from Web)
                    elif cmd_type == "TOGGLE_PIN":
                         params = msg_json.get("params", {})
                         state_val = 1 if params.get("state") == "ON" else 0
                         target = params.get("target_id", 1)
                         pin = params.get("gpio")
                         if pin is not None:
                             frame = self.protocol.pack_frame(SetGpio(target_id=target, pin=pin, value=state_val))
                             await self._send_protocol_cmd(frame)
                             response_obj = ActionResponse(status="OK", message="Toggle Sent")
                    
                    else:
                        # self.logger.warning(f"Unknown Command Type: {cmd_type}")
                        # Don't error out loudly, maybe just ignore or basic Ack
                        response_obj = ActionResponse(status="ERROR", message="Unknown Command Type")

                    if response_obj:
                        writer.write(response_obj.model_dump_json().encode() + b'\n')
                        await writer.drain()

                except ValidationError as e:
                    err = ActionResponse(status="ERROR", message=f"Schema Error: {e}")
                    writer.write(err.model_dump_json().encode() + b'\n')
                    await writer.drain()
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    self.logger.error(f"Processing Error: {e}")
                
        except Exception as e:
            self.logger.error(f"Client Error: {e}")
        finally:
            self.logger.info(f"[NET] Client Disconnected: {addr}")
            self.clients.discard(writer)
            try: writer.close()
            except: pass

    async def _send_protocol_cmd(self, data: bytes):
        if self.transport:
            await self.transport.send(data)

if __name__ == "__main__":
    service = DemeterService()
    try:
        asyncio.run(service.start())
    except KeyboardInterrupt:
        pass
