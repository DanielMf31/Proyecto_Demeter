import asyncio
import json
import logging
import os
from typing import Callable, Optional, List, Dict
from ..shared.schemas import GpioCommand, ActionResponse, PingCommand, SequenceCommand, SequenceStep, GetSensorsCommand

class DemeterViewModel:
    """
    Manages the application state and async communication.
    Decoupled from CustomTkinter (UI agnostic).
    """
    def __init__(self, loop: asyncio.AbstractEventLoop, log_callback: Callable[[str], None], status_callback: Callable[[bool], None], data_callback: Callable[[object], None] = None):
        self.loop = loop
        self.writer = None
        self.reader = None
        self.connected = False
        
        # Callbacks to update UI
        self._log_cb = log_callback
        self._status_cb = status_callback
        self._data_cb = data_callback
        
        self.host = os.getenv('DEMETER_HOST', '127.0.0.1')
        self.port = int(os.getenv('DEMETER_SOCKET_PORT', 8888))
        
        self._seq_dir = os.path.join(os.getcwd(), "sequences")
        os.makedirs(self._seq_dir, exist_ok=True)

    async def connect(self):
        """Attempts to connect to the backend service."""
        while not self.connected:
            try:
                self.log(f"Connecting to {self.host}:{self.port}...")
                self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
                self.connected = True
                self._status_cb(True)
                self.log("CONNECTED to Demeter Service")
                
            except Exception as e:
                self.log(f"Connection Failed: {e}. Retrying in 3s...")
                self._status_cb(False)
                await asyncio.sleep(3)

    async def send_command(self, pin: int, action: str):
        """Sends a GPIO command to the service."""
        if not self.connected or not self.writer:
            self.log("Warning: Not connected. Command queued/dropped.")
            return

        try:
            cmd = GpioCommand(pin=pin, action=action)
            json_str = cmd.model_dump_json()
            
            self.writer.write(json_str.encode())
            await self.writer.drain()
            self.log(f"TX: {action} PIN {pin}")
            
            # Wait for ACK (Request-Response pattern)
            data = await self.reader.read(1024)
            if data:
                self._handle_response(data)
            else:
                 self.log("Warning: Connection closed by server.")
                 self.connected = False
                 self._status_cb(False)
                 asyncio.create_task(self.connect())

        except Exception as e:
            self.log(f"TX Error: {e}")
            self.connected = False
            self._status_cb(False)
            asyncio.create_task(self.connect())

    async def send_ping(self, target_id: int):
        """Sends a Ping command."""
        if not self.connected: return
        try:
            cmd = PingCommand(target_id=target_id)
            await self._send_json(cmd)
            self.log(f"TX: PING Node {target_id}")
        except Exception as e:
            self.log(f"TX Error: {e}")

    async def send_get_sensors(self, target_id: int):
        """Requests sensor data from a node."""
        if not self.connected: return
        try:
            cmd = GetSensorsCommand(target_id=target_id)
            await self._send_json(cmd)
            self.log(f"TX: GET_SENSORS Node {target_id}")
        except Exception as e:
            self.log(f"TX Error: {e}")

    async def send_sequence(self, steps: list, target_id: int = 1):
        """Sends a Sequence command."""
        if not self.connected: return
        try:
            # steps is list of SequenceStep objects (Pydantic models)
            cmd = SequenceCommand(steps=steps, target_id=target_id)
            await self._send_json(cmd)
            self.log(f"TX: SEQUENCE ({len(steps)} steps)")
        except Exception as e:
            self.log(f"TX Error: {e}")

    async def _send_json(self, model):
        """Helper to send Pydantic models as JSON."""
        if self.writer:
            json_str = model.model_dump_json()
            self.writer.write(json_str.encode())
            await self.writer.drain()
            # Wait for response
            data = await self.reader.read(1024)
            if data:
                self._handle_response(data)

    def _handle_response(self, data: bytes):
        try:
            resp_str = data.decode().strip()
            messages = resp_str.replace('}{', '}\n{').split('\n')
            
            for msg in messages:
                if not msg: continue
                try:
                    data_json = json.loads(msg)
                    
                    # 1. Check if it is a DataReport
                    if "temperature" in data_json and "humidity" in data_json:
                        node = data_json.get("node_id", "?")
                        temp = data_json.get("temperature", 0.0)
                        hum = data_json.get("humidity", 0.0)
                        self.log(f"[RPT] Node {node}: {temp}C | {hum}%")
                        
                        if self._data_cb:
                            # Pass the raw dict or the Pydantic model? 
                            # Let's pass the Pydantic model for type safety if possible, but here we have dict.
                            # Schemas are imported.
                            try:
                                from ..shared.schemas import DataReport
                                report = DataReport(**data_json)
                                self._data_cb(report)
                            except:
                                pass
                        
                    # 2. Check if it is ActionResponse
                    elif "status" in data_json:
                        resp = ActionResponse.model_validate(data_json)
                        status_text = "[OK]" if resp.status == "OK" else "[ERROR]"
                        self.log(f"RX {status_text}: {resp.message}")
                        
                    else:
                        self.log(f"RX Unknown: {msg}")

                except json.JSONDecodeError:
                    self.log(f"RX Parse Error: {msg}")
                    
        except Exception as e:
            self.log(f"Warning: Invalid RX Processing: {e}")

    def save_sequence_file(self, filename: str, steps: List[Dict]):
        """Saves a sequence logic to JSON."""
        try:
            path = os.path.join(self._seq_dir, filename)
            with open(path, "w") as f:
                json.dump(steps, f, indent=4)
            self.log(f"Saved sequence: {filename}")
        except Exception as e:
            self.log(f"Error saving sequence: {e}")

    def load_sequence_file(self, filename: str) -> Optional[List[Dict]]:
        """Loads a sequence logic from JSON."""
        try:
            path = os.path.join(self._seq_dir, filename)
            if not os.path.exists(path):
                self.log(f"File not found: {filename}")
                return None
            
            with open(path, "r") as f:
                steps = json.load(f)
            
            self.log(f"Loaded sequence: {filename}")
            return steps
        except Exception as e:
            self.log(f"Error loading sequence: {e}")
            return None

    def log(self, text: str):
        """Bridge to UI Logger."""
        if self._log_cb:
            # Simple sanitization filter if strictly needed, 
            # though we removed emojis from source strings.
            # text = text.replace("📊", "").replace("✅", "")
            self._log_cb(text)

    def shutdown(self):
        if self.writer:
            self.writer.close()
