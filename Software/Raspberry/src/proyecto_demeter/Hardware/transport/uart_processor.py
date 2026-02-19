import asyncio
import logging
import os
import sys

# Add project root and Common to sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '../../../../../'))
COMMON_DIR = os.path.join(PROJECT_ROOT, 'Software', 'Common')

sys.path.append(PROJECT_ROOT)
if COMMON_DIR not in sys.path:
    sys.path.append(COMMON_DIR)

try:
    from proyecto_demeter.Hardware.transport.async_uart import AsyncUartTransport
    from demeter_protocol import DemeterProtocolV2
    from schemas import (
        DemeterCommand, ExecSequence, 
        TempHumReport, PinReport, SystemReport, Ack, Nack, CmdId,
        SetGpio, Ping, GetSensors, Syn, SynAck, SetPwm, RouteAdd
    )
    from configuration import settings

except ImportError as e:
    logging.error(f"Import Error in Uart_processor: {e}")
    logging.error(f"Sys Path: {sys.path}")
    raise

# Constants
UART_PORT = settings.PORT
UART_BAUD = settings.UART_BAUD

class UartProcessor:
    """
    Orchestrator for UART Communication.
    - Manages AsyncUartTransport.
    - Parses frames using DemeterProtocolV2.
    - Handles protocol-level logic (Handshakes, ACKs).
    - Dispatches application-level commands to listeners.
    """
    def __init__(self):
        # Configure logging
        handlers = [logging.StreamHandler(sys.stdout)]
        if settings.LOG_FILE_PATH:
             os.makedirs(os.path.dirname(settings.LOG_FILE_PATH), exist_ok=True)
             handlers.append(logging.FileHandler(settings.LOG_FILE_PATH))

        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
            format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            handlers=handlers
        )
        self.logger = logging.getLogger("UartProcessor")
        
        self.transport = None
        self.protocol = DemeterProtocolV2()
        
        # RX Architecture
        self.rx_buffer = bytearray()
        self.rx_queue = asyncio.Queue()
        
        # Listeners for App Logic
        self.listeners = []
        
        # Internal State
        self.running = False
        self.dispatch_task = None

    def add_listener(self, listener):
        """Add a callback for Valid Commands."""
        self.listeners.append(listener)

    async def start(self):
        """Start Transport and Dispatcher."""
        self.logger.info("[START] Starting Demeter UART Processor...")
        self.running = True

        # 1. Start Transport (UART)
        self.transport = AsyncUartTransport(UART_PORT, UART_BAUD)
        self.transport.set_callback(self.on_uart_data)
        
        if await self.transport.connect():
            self.logger.info(f"[HW] UART Connected to {UART_PORT}")
        else:
            self.logger.error("[ERR] UART Connect Failed")
            # We might want to retry or exit, but for now we keep running to allow logic to handle it
        
        # 2. Start Dispatcher (Consumer)
        self.dispatch_task = asyncio.create_task(self._dispatch_loop())

        # 3. Initial Handshake (Example)
        # known_nodes = [2, 3] 
        # for node in known_nodes:
        #    await self.send_command(Syn(target_id=node, context=0))

        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            self.logger.info("Service stopping...")
            await self.stop()

    async def stop(self):
        self.running = False
        if self.transport:
            await self.transport.disconnect()
        if self.dispatch_task:
            self.dispatch_task.cancel()

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
                # Producer: Put valid command into Queue
                try:
                    self.rx_queue.put_nowait(cmd)
                except Exception as e:
                    self.logger.error(f"Queue Full/Error: {e}")
            else:
                self.logger.warning(f"Invalid Frame. Dropping SYNC. Data: {frame_bytes.hex()}")
                del self.rx_buffer[0]

    async def _dispatch_loop(self):
        """Consumer Task: Process commands from Queue."""
        self.logger.info("[CORE] Dispatch Loop Active")
        while True:
            try:
                cmd = await self.rx_queue.get()
                
                # 1. Handle Protocol Logic Internal (ACKs, Handshakes)
                await self.handle_protocol_internal(cmd)
                
                # 2. Forward to Listeners (Business Logic)
                for listener in self.listeners:
                    try:
                        if asyncio.iscoroutinefunction(listener):
                            await listener(cmd)
                        else:
                            listener(cmd)
                    except Exception as e:
                        self.logger.error(f"Listener Exception: {e}")

                self.rx_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Dispatch Error: {e}")

    async def handle_protocol_internal(self, cmd: DemeterCommand):
        """
        Handle internal protocol logic:
        - Reply to PING with ACK (or Pong)
        - Reply to SYN with SYN-ACK
        - Reply to SYN-ACK with ACK
        """
        if isinstance(cmd, Ping):
            self.logger.info(f"[RX] PING from {cmd.source_id}")
            await self.send_ack(cmd.source_id, CmdId.PING)

        elif isinstance(cmd, Syn):
            self.logger.info(f"[RX] SYN from {cmd.source_id}. Sending SYN-ACK.")
            await self.send_syn_ack(cmd.source_id, cmd.context)

        elif isinstance(cmd, SynAck):
            self.logger.info(f"[RX] SYN-ACK from {cmd.source_id}. Handshake Complete. Sending ACK.")
            await self.send_ack(cmd.source_id, CmdId.SYN_ACK)

        elif isinstance(cmd, Ack):
            self.logger.debug(f"[RX] ACK from {cmd.source_id} for CMD {cmd.original_cmd_id}")

        elif isinstance(cmd, Nack):
            self.logger.warning(f"[RX] NACK from {cmd.source_id} for CMD {cmd.original_cmd_id} (Err: {cmd.error_code})")
        
        # Reports -> Listeners
        elif isinstance(cmd, (TempHumReport, PinReport, SystemReport)):
            pass 

    # --- Start of Helper Send Methods ---
    async def send_ack(self, target_id: int, original_cmd_id: int):
        await self.send_command(Ack(target_id=target_id, original_cmd_id=original_cmd_id))

    async def send_nack(self, target_id: int, original_cmd_id: int, error_code: int):
        await self.send_command(Nack(target_id=target_id, original_cmd_id=original_cmd_id, error_code=error_code))

    async def send_syn(self, target_id: int, context: int = 0):
        await self.send_command(Syn(target_id=target_id, context=context))

    async def send_syn_ack(self, target_id: int, context: int = 0):
        await self.send_command(SynAck(target_id=target_id, context=context))

    async def send_ping(self, target_id: int):
        await self.send_command(Ping(target_id=target_id))

    async def send_set_gpio(self, target_id: int, pin: int, value: bool, flags: int = 0):
        await self.send_command(SetGpio(target_id=target_id, pin=pin, value=int(value), flags=flags))
    
    async def send_get_sensors(self, target_id: int):
         await self.send_command(GetSensors(target_id=target_id))
    # ------------------------------------

    async def send_command(self, cmd: DemeterCommand):
        """Helper to send a command via UART."""
        if self.transport:
            try:
                frame = self.protocol.pack_frame(cmd)
                await self.transport.send(frame)
            except Exception as e:
                self.logger.error(f"Send Error: {e}")

if __name__ == "__main__":
    processor = UartProcessor()
    
    # Simple example listener
    async def debug_listener(cmd):
        if not isinstance(cmd, (Ack, Syn, SynAck, Ping)):
            print(f"[APP] Received: {cmd}")

    processor.add_listener(debug_listener)

    try:
        asyncio.run(processor.start())
    except KeyboardInterrupt:
        pass
