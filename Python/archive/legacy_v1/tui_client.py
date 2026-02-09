from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Log, Input, Button, Label, DataTable
from textual import work
from textual.message import Message
import asyncio
import json
import logging

SOCKET_HOST = '127.0.0.1'
SOCKET_PORT = 8888

class DemeterTui(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    .box {
        height: 100%;
        border: solid green;
    }
    #sidebar {
        width: 30%;
        dock: left;
        background: $panel;
    }
    #main_log {
        width: 70%;
        height: 100%;
        background: $boost;
    }
    DataTable {
        height: 50%;
    }
    """
    TITLE = "Demeter V2 Control (Async)"
    SUB_TITLE = "Connected to 127.0.0.1:8888"

    def __init__(self):
        super().__init__()
        self.reader = None
        self.writer = None
        self.connected = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Horizontal(
            Vertical(
                Label("📡 Telemetry", classes="header"),
                DataTable(id="telemetry_table"),
                Label("🎮 Controls", classes="header"),
                Button("Ping Node 2", id="btn_ping_2", variant="primary"),
                Button("Ping Host", id="btn_ping_0", variant="success"),
                Input(placeholder="Send Raw Command...", id="cmd_input"),
                id="sidebar",
                classes="box"
            ),
            Log(id="main_log", classes="box")
        )

    def on_mount(self) -> None:
        self.query_one(Log).write("Initializing TUI...")
        self.setup_table()
        # Start connection in background
        self.connect_to_service()

    def setup_table(self):
        table = self.query_one(DataTable)
        table.add_columns("Node", "Temp (°C)", "Hum (%)", "Last Update")
        table.add_row("2", "--", "--", "--", key="node_2")

    @work(exclusive=True)
    async def connect_to_service(self):
        log = self.query_one(Log)
        while not self.connected:
            try:
                log.write(f"Connecting to {SOCKET_HOST}:{SOCKET_PORT}...")
                self.reader, self.writer = await asyncio.open_connection(SOCKET_HOST, SOCKET_PORT)
                self.connected = True
                log.write("✅ Connected to Service!")
                # Start listener
                asyncio.create_task(self.listen_loop())
            except Exception as e:
                log.write(f"❌ Connection Failed: {e}. Retrying in 2s...")
                await asyncio.sleep(2)

    async def listen_loop(self):
        log = self.query_one(Log)
        try:
            while True:
                data = await self.reader.readline()
                if not data: break
                
                line = data.decode().strip()
                if not line: continue
                
                try:
                    msg = json.loads(line)
                    self.process_message(msg)
                except json.JSONDecodeError:
                    log.write(f"RX Raw: {line}")
        except Exception as e:
            log.write(f"Create read error: {e}")
            self.connected = False

    def process_message(self, msg):
        log = self.query_one(Log)
        msg_type = msg.get("type")
        payload = msg.get("payload", {})

        if msg_type == "RX_FRAME":
            # It's a protocol frame
            self.handle_protocol_frame(payload)
        else:
            log.write(f"EVENT: {msg}")

    def handle_protocol_frame(self, frame_dict):
        log = self.query_one(Log)
        # We need to guess the type from the dict fields provided by Pydantic
        # Or simpler: just log it for now
        
        # Check if it looks like DataReport
        if "temperature" in frame_dict and "humidity" in frame_dict:
             node_id = frame_dict.get("node_id", "?")
             self.update_telemetry(node_id, frame_dict["temperature"], frame_dict["humidity"])
             log.write(f"🌡️ DATA: Node {node_id} | {frame_dict['temperature']}°C {frame_dict['humidity']}%")
        # Check if Ping/Ack
        elif "source_id" in frame_dict:
             log.write(f"RX Frame: {frame_dict}")
        else:
             log.write(f"RX: {frame_dict}")

    def update_telemetry(self, node_id, temp, hum):
        table = self.query_one(DataTable)
        import datetime
        now = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Check if row exists
        row_key = f"node_{node_id}"
        if table.is_valid_row_index(0): # Try to update if exists (Mock logic for now)
             try:
                table.update_cell(row_key, "Temp (°C)", str(temp))
                table.update_cell(row_key, "Hum (%)", str(hum))
                table.update_cell(row_key, "Last Update", now)
             except:
                # Add new
                table.add_row(str(node_id), str(temp), str(hum), now, key=row_key)
        else:
             table.add_row(str(node_id), str(temp), str(hum), now, key=row_key)

    async def send_command(self, cmd_type, payload):
        if not self.writer: return
        
        msg = {
            "type": cmd_type,
            "payload": payload
        }
        data = (json.dumps(msg) + "\n").encode()
        self.writer.write(data)
        await self.writer.drain()
        self.query_one(Log).write(f"TX -> {cmd_type} {payload}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn_ping_2":
            await self.send_command("PING", {"target_id": 2})
        elif btn_id == "btn_ping_0":
            await self.send_command("PING", {"target_id": 0})

if __name__ == "__main__":
    app = DemeterTui()
    app.run()
