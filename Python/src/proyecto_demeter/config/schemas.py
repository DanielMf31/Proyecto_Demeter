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
    
    # Reports
    TEMP_HUM_REPORT = 0x0B  # Replaces DataReport
    PIN_REPORT      = 0x0C  # New: GPIO State Feedback
    SYSTEM_REPORT   = 0x0D  # New: System Mode + Battery
    
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

@dataclass
class SequenceConfig:
    """Configuration for a sequence of steps"""
    steps: List[SequenceStep]
    name: str = "default_sequence"

class ExecSequence(DemeterCommand):
    steps: List[SequenceStep] = Field(min_length=1, max_length=30)
    def get_cmd_id(self) -> int: return CmdId.EXEC_SEQUENCE

# --- Reports (New Modular Types) ---

class TempHumReport(DemeterCommand):
    """Environmental Data (DHT22, etc.)"""
    node_id: int = Field(..., ge=0, le=254)
    temperature: float
    humidity: float
    timestamp: float = 0.0 # Epoch time (Added by Gateway/Server)

    def get_cmd_id(self) -> int: return CmdId.TEMP_HUM_REPORT

class PinReport(DemeterCommand):
    """Feedback for GPIO State Change"""
    node_id: int = Field(..., ge=0, le=254)
    pin: int = Field(ge=0, le=40)
    state: int = Field(ge=0, le=1) # 0=OFF, 1=ON (uint8)

    def get_cmd_id(self) -> int: return CmdId.PIN_REPORT

class SystemReport(DemeterCommand):
    """System Health & Mode"""
    node_id: int = Field(..., ge=0, le=254)
    mode: int = Field(ge=0, le=255) # 0=Active, 1=LightSleep, 2=DeepSleep
    battery_mv: int = Field(ge=0, le=65535) # Voltage in mV
    reserved: bytes = Field(default=b'\x00'*5, min_length=5, max_length=5) # 5 Bytes Reserved

    def get_cmd_id(self) -> int: return CmdId.SYSTEM_REPORT

# ==========================================
# GUI/API Communication Models (JSON)
# ==========================================
class GpioCommand(BaseModel):
    type: Literal["GPIO_CMD"] = "GPIO_CMD"
    pin: int = Field(..., ge=0, le=40)
    action: Literal["ON", "OFF", "TOGGLE"]

class PingCommand(BaseModel):
    type: Literal["PING_CMD"] = "PING_CMD"
    target_id: int = Field(..., ge=0, le=254)

class GetSensorsCommand(BaseModel):
    type: Literal["GET_SENSORS_CMD"] = "GET_SENSORS_CMD"
    target_id: int = Field(..., ge=0, le=254)

class SequenceCommand(BaseModel):
    type: Literal["SEQ_CMD"] = "SEQ_CMD"
    steps: List[SequenceStep]
    target_id: int = Field(default=1)

class ActionResponse(BaseModel):
    status: Literal["OK", "ERROR"]
    message: str
    pin_state: Optional[bool] = None
    data: Optional[dict] = None

class LogMessage(BaseModel):
    type: Literal["LOG"] = "LOG"
    level: str
    message: str
    timestamp: float

class SequenceFile(BaseModel):
    name: str
    description: str
    steps: List[SequenceStep]
