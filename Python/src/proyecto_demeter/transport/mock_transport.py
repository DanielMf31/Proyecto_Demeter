import asyncio
import logging
import random
import struct
from typing import Callable, Optional, List, Dict
from abc import ABC, abstractmethod
from ..protocols.protocol_v2 import DemeterProtocolV2
from ..config.schemas import (
    CmdId, SetGpio, Ping, Ack, DemeterCommand, 
    TempHumReport, PinReport, SystemReport
)

# ==========================================
# Strategy Interface
# ==========================================
class MockStrategy(ABC):
    def __init__(self, transport: 'MockTransport'):
        self.transport = transport
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    async def handle_command(self, cmd: DemeterCommand):
        """Handle incoming commands from the host."""
        pass

    @abstractmethod
    async def run_loop(self):
        """Run periodic tasks (background simulation)."""
        pass

# ==========================================
# Concrete Strategies
# ==========================================
class SensorStrategy(MockStrategy):
    def __init__(self, transport: 'MockTransport'):
        super().__init__(transport)
        self.simulated_nodes = [
            {"id": 10, "temp": 24.0, "hum": 50.0},
            {"id": 11, "temp": 22.5, "hum": 45.0}
        ]

    async def handle_command(self, cmd: DemeterCommand):
        pass

    async def run_loop(self):
        while self.transport.running:
            try:
                await asyncio.sleep(5.0)
                # Random Sensor Report
                node = random.choice(self.simulated_nodes)
                node["temp"] += random.uniform(-0.5, 0.5)
                
                # Clamp values
                node["temp"] = max(10.0, min(40.0, node["temp"]))

                report = TempHumReport(
                    target_id=0, 
                    node_id=node["id"], 
                    temperature=node["temp"], 
                    humidity=node["hum"]
                )
                self.logger.info(f"[MOCK SENSOR] Node {node['id']} Temp={node['temp']:.1f}")
                self.transport.send_frame_to_host(self.transport.protocol.serialize(report))
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Sensor Loop Error: {e}")

class ActuatorStrategy(MockStrategy):
    def __init__(self, transport: 'MockTransport'):
        super().__init__(transport)
        self.actuator_id = 3
        self.gpio_state = 0
        self.battery_mv = 12600 # 12.6V in mV

    async def handle_command(self, cmd: DemeterCommand):
        # Filter for Actuator or Gateway (Target 1 or 3)
        if cmd.target_id not in [self.actuator_id, 1]:
            return

        if isinstance(cmd, SetGpio):
            self.logger.info(f"[MOCK ACTUATOR] SET_GPIO Pin={cmd.pin} Val={cmd.value}")
            
            # Simulate Hardware Delay
            await asyncio.sleep(0.2)
            
            # Update State
            self.gpio_state = cmd.value
            self.battery_mv -= 50 # Drain battery
            
            # Reply with Pin Feedback
            pin_report = PinReport(
                target_id=0,
                node_id=self.actuator_id,
                pin=cmd.pin,
                state=self.gpio_state
            )
            self.transport.send_frame_to_host(self.transport.protocol.serialize(pin_report))
            self.logger.info("[MOCK ACTUATOR] Sent Pin Report")

        elif isinstance(cmd, Ping):
            self.logger.info(f"[MOCK ACTUATOR] PING received")
            ack = Ack(target_id=cmd.target_id, original_cmd_id=CmdId.PING)
            self.transport.send_frame_to_host(self.transport.protocol.serialize(ack))

    async def run_loop(self):
        # Actuator might send a heartbeat occasionally
        while self.transport.running:
            try:
                await asyncio.sleep(15.0)
                # Heartbeat?
            except asyncio.CancelledError:
                break

class MixedStrategy(MockStrategy):
    def __init__(self, transport: 'MockTransport'):
        super().__init__(transport)
        self.sensor_strategy = SensorStrategy(transport)
        self.actuator_strategy = ActuatorStrategy(transport)

    async def handle_command(self, cmd: DemeterCommand):
        # Delegation
        await self.actuator_strategy.handle_command(cmd)
        await self.sensor_strategy.handle_command(cmd)

    async def run_loop(self):
        # Run both loops concurrently
        await asyncio.gather(
            self.sensor_strategy.run_loop(),
            self.actuator_strategy.run_loop()
        )

# ==========================================
# Main Context
# ==========================================
class MockTransport:
    """
    Simulates a UART connection using selectable Strategies.
    """
    def __init__(self, port: str = "MOCK", baudrate: int = 115200, mode: str = "MIXED"):
        self.logger = logging.getLogger("MockTransport")
        self.mode = mode.upper()
        self.running = False
        self.callback: Optional[Callable[[bytes], None]] = None
        self.task = None
        
        self.protocol = DemeterProtocolV2()
        
        # Factory
        self.strategy: MockStrategy
        if self.mode == "SENSORS":
            self.strategy = SensorStrategy(self)
        elif self.mode == "ACTUATOR":
            self.strategy = ActuatorStrategy(self)
        else:
            self.strategy = MixedStrategy(self)
            
        self.logger.info(f"[MOCK] Initialized with Strategy: {self.strategy.__class__.__name__}")

    def set_callback(self, callback: Callable[[bytes], None]):
        self.callback = callback

    async def connect(self) -> bool:
        self.logger.info("[MOCK] Connected to Virtual UART")
        self.running = True
        self.task = asyncio.create_task(self.strategy.run_loop())
        return True

    async def send(self, data: bytes):
        """Handle outgoing data from Host -> Device"""
        try:
            cmd = self.protocol.parse_frame(data)
            if cmd:
                await self.strategy.handle_command(cmd)
            else:
                self.logger.warning("[MOCK] Received invalid frame")
        except Exception as e:
            self.logger.error(f"[MOCK] Parse Error: {e}")

    def send_frame_to_host(self, data: bytes):
        """Called by strategies to send data upstream."""
        if self.callback:
            self.callback(data)

    async def close(self):
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.logger.info("[MOCK] Disconnected")
