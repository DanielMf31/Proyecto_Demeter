import asyncio
import logging
import random
import struct
from typing import Callable, Optional

# Re-use Protocol constants if possible, or redefine to avoid circular deps if protocol imports transport
# Usually Protocol imports schemas, Transport is independent.
# We need to construct VALID frames, so we need similar packing logic or use the Protocol class helper?
# To simulate "Raw" bytes, we should manually pack or use a simplified packer to avoid dependency on the full Protocol parser logic if we want to test that too.
# But reusing Protocol.serialize is smart to ensure validity.

# However, to avoid circular imports (Service imports Transport, Service imports Protocol), 
# Transport should NOT import Protocol if Protocol imports Transport (it usually doesn't).
# Let's see: `protocol_v2` does not import transport. So we can import Protocol here.

from ..protocols.protocol_v2 import DemeterProtocolV2
from ..shared.schemas import DataReport, CmdId

class MockTransport:
    """
    Simulates a UART connection by generating synthetic traffic.
    """
    def __init__(self, port: str = "MOCK", baudrate: int = 115200):
        self.logger = logging.getLogger("MockTransport")
        self.running = False
        self.callback: Optional[Callable[[bytes], None]] = None
        self.task = None
        
        # Simulation State
        self.simulated_nodes = [
            {"id": 10, "temp": 24.0, "hum": 50.0},
            {"id": 11, "temp": 22.5, "hum": 45.0},
            {"id": 12, "temp": 26.0, "hum": 60.0}
        ]
        
        # Helper for packing
        self.protocol = DemeterProtocolV2()

    def set_callback(self, callback: Callable[[bytes], None]):
        self.callback = callback

    async def connect(self) -> bool:
        self.logger.info("🔌 [MOCK] Connected to Virtual UART")
        self.running = True
        self.task = asyncio.create_task(self._simulation_loop())
        return True

    async def send(self, data: bytes):
        """Log outgoing bytes."""
        # self.logger.debug(f"TX [MOCK]: {data.hex()}")
        # We could parse this to react (e.g. if we send SET_GPIO, we could log it)
        pass

    async def close(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.logger.info("🔌 [MOCK] Disconnected")

    async def _simulation_loop(self):
        self.logger.info("🎲 [MOCK] Starting Data Generation...")
        while self.running:
            try:
                await asyncio.sleep(2.0) # Report every 2 seconds
                
                # Pick a random node
                node = random.choice(self.simulated_nodes)
                
                # Update physics (Random Walk)
                node["temp"] += random.uniform(-0.5, 0.5)
                node["hum"] += random.uniform(-1.0, 1.0)
                
                # Clamp
                node["temp"] = max(10.0, min(40.0, node["temp"]))
                node["hum"] = max(20.0, min(90.0, node["hum"]))
                
                # Create Packet
                report = DataReport(
                    target_id=1, # Gateway
                    node_id=node["id"], 
                    temperature=node["temp"], 
                    humidity=node["hum"]
                )
                
                # Serialize to Bytes using Protocol V2
                frame_bytes = self.protocol.serialize(report)
                
                # Push availability to callback
                if self.callback:
                    self.callback(frame_bytes)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Simulation Error: {e}")
                await asyncio.sleep(1)
