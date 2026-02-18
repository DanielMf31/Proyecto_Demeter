from enum import IntEnum
from typing import List, Optional, Literal, Union, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field, ValidationError

# ==========================================
# Enums (Protocol Constants)
# ==========================================
class CmdId(IntEnum):
    PING            = 0x01
    ACK             = 0x02
    NACK            = 0x03
    SYN             = 0x04
    SYN_ACK         = 0x05
    ROUTE_ADD       = 0x0A
    
    # Reports
    TEMP_HUM_REPORT = 0x0B
    PIN_REPORT      = 0x0C
    SYSTEM_REPORT   = 0x0D
    
    # Commands
    SET_GPIO        = 0x10
    SET_PWM         = 0x11
    GET_SENSORS     = 0x20
    EXEC_SEQUENCE   = 0x30

# ==========================================
# Protocol V2 Models (Binary Structure Abstraction)
# ==========================================
class DemeterCommand(BaseModel):
    """Base class for all Protocol Commands."""
    target_id: int = Field(ge=0, le=254, description="Node ID of the recipient")
    source_id: Optional[int] = Field(default=None, ge=0, le=255, description="Node ID of the sender")
    
    def get_cmd_id(self) -> int:
        raise NotImplementedError("Subclasses must implement get_cmd_id")

# --- Control Commands ---
class Ping(DemeterCommand):
    def get_cmd_id(self) -> int: return CmdId.PING

class Ack(DemeterCommand):
    original_cmd_id: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.ACK

class Nack(DemeterCommand):
    original_cmd_id: int = Field(ge=0, le=255)
    error_code: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.NACK

class Syn(DemeterCommand):
    context: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SYN

class SynAck(DemeterCommand):
    context: int = Field(default=0, ge=0, le=255) 
    def get_cmd_id(self) -> int: return CmdId.SYN_ACK

class SetGpio(DemeterCommand):
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    flags: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SET_GPIO

class SetPwm(DemeterCommand):
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=65535)
    def get_cmd_id(self) -> int: return CmdId.SET_PWM

class GetSensors(DemeterCommand):
    def get_cmd_id(self) -> int: return CmdId.GET_SENSORS

class RouteAdd(DemeterCommand):
    node_id_to_register: int = Field(ge=0, le=254)
    mac_address_bytes: bytes = Field(min_length=6, max_length=6)
    def get_cmd_id(self) -> int: return CmdId.ROUTE_ADD

# --- Sequence Structures ---
class SequenceStep(BaseModel):
    target_id: int = Field(default=1, ge=0, le=254)
    cmd_id: int = Field(default=CmdId.SET_GPIO.value)
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    delay_ms: int = Field(ge=0, le=4294967295)

class ExecSequence(DemeterCommand):
    steps: List[SequenceStep] = Field(min_length=1, max_length=30)
    def get_cmd_id(self) -> int: return CmdId.EXEC_SEQUENCE

# --- Reports ---

class TempHumReport(DemeterCommand):
    node_id: int = Field(..., ge=0, le=254)
    temperature: float
    humidity: float
    timestamp: float = 0.0
    def get_cmd_id(self) -> int: return CmdId.TEMP_HUM_REPORT

class PinReport(DemeterCommand):
    node_id: int = Field(..., ge=0, le=254)
    pin: int = Field(ge=0, le=40)
    state: int = Field(ge=0, le=1)
    def get_cmd_id(self) -> int: return CmdId.PIN_REPORT

class SystemReport(DemeterCommand):
    node_id: int = Field(..., ge=0, le=254)
    mode: int = Field(ge=0, le=255)
    battery_mv: int = Field(ge=0, le=65535)
    reserved: bytes = Field(default=b'\x00'*5, min_length=5, max_length=5)
    def get_cmd_id(self) -> int: return CmdId.SYSTEM_REPORT

# ==========================================
# JSON Command Models (Frontend -> Backend -> IoT)
# ==========================================

class ActionResponse(BaseModel):
    status: str
    message: str

class GpioCommand(BaseModel):
    type: Literal["GPIO_CMD"] = "GPIO_CMD"
    target_id: int
    pin: int
    action: Literal["ON", "OFF"]

class PingCommand(BaseModel):
    type: Literal["PING_CMD"] = "PING_CMD"
    target_id: int

class GetSensorsCommand(BaseModel):
    type: Literal["GET_SENSORS_CMD"] = "GET_SENSORS_CMD"
    target_id: int

class SequenceCommand(BaseModel):
    type: Literal["SEQ_CMD"] = "SEQ_CMD"
    target_id: int
    steps: List[SequenceStep]

class JsonCommand(BaseModel):
    """
    Standard format for commands sent via WebSocket/JSON.
    Example: { "type": "command", "command": "TOGGLE_PIN", "params": { "gpio": 4, "state": "ON" } }
    """
    type: str # Relaxed from Literal to allow more flexibility during dev
    command: Optional[str] = None
    params: Dict[str, Any] = {}
