from enum import IntEnum
from typing import List, Optional, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field

# ==========================================
# Enums
# ==========================================
class CmdId(IntEnum):
    PING            = 0x01
    ACK             = 0x02
    NACK            = 0x03
    ROUTE_ADD       = 0x0A
    DATA_REPORT     = 0x0B
    SET_GPIO        = 0x10
    SET_PWM         = 0x11
    GET_SENSORS     = 0x20
    EXEC_SEQUENCE   = 0x30

# ==========================================
# Base Models
# ==========================================
class DemeterCommand(BaseModel):
    """Base class for all Protocol Commands."""
    target_id: int = Field(ge=0, le=254, description="Node ID of the recipient")
    
    def get_cmd_id(self) -> int:
        raise NotImplementedError("Subclasses must implement get_cmd_id")

# ==========================================
# Specific Commands
# ==========================================
class Ack(DemeterCommand):
    """Positive Acknowledgment."""
    original_cmd_id: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.ACK

class Nack(DemeterCommand):
    """Negative Acknowledgment."""
    original_cmd_id: int = Field(ge=0, le=255)
    error_code: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.NACK

class Ping(DemeterCommand):
    def get_cmd_id(self) -> int: return CmdId.PING

class SetGpio(DemeterCommand):
    """Directly control a digital pin."""
    pin: int = Field(ge=0, le=40, description="Physical GPIO Pin Number")
    value: int = Field(ge=0, le=1, description="1=High, 0=Low")
    flags: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SET_GPIO

class SetPwm(DemeterCommand):
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=65535, description="PWM Duty Cycle 16-bit")
    def get_cmd_id(self) -> int: return CmdId.SET_PWM

class RouteAdd(DemeterCommand):
    """Register a route (Mac Address) in the Gateway."""
    node_id_to_register: int = Field(ge=0, le=254)
    # 6 bytes for MAC
    mac_address_bytes: bytes = Field(min_length=6, max_length=6)
    def get_cmd_id(self) -> int: return CmdId.ROUTE_ADD

# ==========================================
# Sequence Structures
# ==========================================
class SequenceStep(BaseModel):
    """
    A single step in a batch execution.
    Unified model: Contains Protocol fields (target, cmd) and UI fields (pin, val, delay).
    """
    target_id: int = Field(default=1, ge=0, le=254, description="Target Node ID (1=Gateway)")
    cmd_id: int = Field(default=CmdId.SET_GPIO.value, description="Command ID (Default: SetGpio)")
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    delay_ms: int = Field(ge=0, le=4294967295, description="Delay after execution (ms)")

@dataclass
class SequenceConfig:
    """Configuration for a sequence of steps"""
    steps: List[SequenceStep]
    name: str = "default_sequence"

@dataclass
class DataReport:
    """Sensor Data Report from Node"""
    node_id: int
    temperature: float
    humidity: float
    timestamp: float = 0.0 # Epoch time

class ExecSequence(DemeterCommand):
    steps: List[SequenceStep] = Field(min_length=1, max_length=30)
    def get_cmd_id(self) -> int: return CmdId.EXEC_SEQUENCE

class SequenceFile(BaseModel):
    """
    Metadata and content for a saved sequence file.
    """
    name: str = Field(..., min_length=1, description="Display Name")
    description: str = Field("", description="Optional Description")
    steps: List[SequenceStep]
