from enum import IntEnum
from typing import List, Optional, Literal, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field

# ==========================================
# Enums (Protocol Constants)
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
# GUI <-> Service Communication Models
# ==========================================
class GpioCommand(BaseModel):
    """
    Command sent by the Client (GUI/TUI) to control hardware via Service.
    Maps conceptually to SetGpio but is JSON-friendly for TCP.
    """
    type: Literal["GPIO_CMD"] = "GPIO_CMD"
    pin: int = Field(..., ge=0, le=40, description="Physical ESP32 Pin Number")
    action: Literal["ON", "OFF", "TOGGLE"] = Field(..., description="Action to perform")

class PingCommand(BaseModel):
    """
    Command sent by GUI to request a Ping to a specific node.
    """
    type: Literal["PING_CMD"] = "PING_CMD"
    target_id: int = Field(..., ge=0, le=254)

class SequenceCommand(BaseModel):
    """
    Command sent by GUI to execute a sequence.
    """
    type: Literal["SEQ_CMD"] = "SEQ_CMD"
    steps: List['SequenceStep']
    target_id: int = Field(default=1)

class ActionResponse(BaseModel):
    """
    Response from the Backend confirming the action.
    """
    status: Literal["OK", "ERROR"]
    message: str
    pin_state: Optional[bool] = None # True=ON, False=OFF, None=Unknown
    data: Optional[dict] = None # For returning sensor data or ping stats

class LogMessage(BaseModel):
    """
    Streamed log message from Service to GUI.
    """
    type: Literal["LOG"] = "LOG"
    level: str
    message: str
    timestamp: float

# ==========================================
# Protocol V2 Models (Binary Structure Abstraction)
# ==========================================
class DemeterCommand(BaseModel):
    """Base class for all Protocol Commands."""
    target_id: int = Field(ge=0, le=254, description="Node ID of the recipient")
    
    def get_cmd_id(self) -> int:
        raise NotImplementedError("Subclasses must implement get_cmd_id")

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
    mac_address_bytes: bytes = Field(min_length=6, max_length=6)
    def get_cmd_id(self) -> int: return CmdId.ROUTE_ADD

# ==========================================
# Sequence Structures
# ==========================================
class SequenceStep(BaseModel):
    """
    A single step in a batch execution.
    """
    target_id: int = Field(default=1, ge=0, le=254, description="Target Node ID (1=Gateway)")
    cmd_id: int = Field(default=CmdId.SET_GPIO.value, description="Command ID (Default: SetGpio)")
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    delay_ms: int = Field(ge=0, le=4294967295, description="Delay after execution (ms)")

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

class DataReport(DemeterCommand):
    """Sensor Data Report from Node"""
    node_id: int = Field(..., ge=0, le=254)
    temperature: float
    humidity: float
    timestamp: float = 0.0 # Epoch time

    def get_cmd_id(self) -> int: return CmdId.DATA_REPORT
