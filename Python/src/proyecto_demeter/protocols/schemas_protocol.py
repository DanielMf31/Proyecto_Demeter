from enum import IntEnum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator

# ==========================================
# Enums
# ==========================================
class CmdId(IntEnum):
    PING            = 0x01
    ACK             = 0x02
    NACK            = 0x03
    ROUTE_ADD       = 0x0A
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
    """
    Positive Acknowledgment of a command.
    Payload: [ORIGINAL_CMD_ID]
    """
    original_cmd_id: int = Field(ge=0, le=255)

    def get_cmd_id(self) -> int:
        return CmdId.ACK

class Nack(DemeterCommand):
    """
    Negative Acknowledgment (Error).
    Payload: [ORIGINAL_CMD_ID] [ERROR_CODE]
    """
    original_cmd_id: int = Field(ge=0, le=255)
    error_code: int = Field(ge=0, le=255)

    def get_cmd_id(self) -> int:
        return CmdId.NACK

class Ping(DemeterCommand):
    def get_cmd_id(self) -> int:
        return CmdId.PING

class SetGpio(DemeterCommand):
    """
    Directly control a digital pin.
    """
    pin: int = Field(ge=0, le=40, description="Physical GPIO Pin Number")
    value: int = Field(ge=0, le=1, description="1=High, 0=Low")
    flags: int = Field(default=0, ge=0, le=255)

    def get_cmd_id(self) -> int:
        return CmdId.SET_GPIO

class SetPwm(DemeterCommand):
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=65535, description="PWM Duty Cycle 16-bit")

    def get_cmd_id(self) -> int:
        return CmdId.SET_PWM

class RouteAdd(DemeterCommand):
    """
    Register a route (Mac Address) in the Gateway.
    Note: target_id in the *Command* is the node being registered.
    But the *Frame* usually targets the Gateway (ID 1).
    This ambiguity is handled by business logic, but structurally this payload 
    carries the ID and MAC.
    """
    node_id_to_register: int = Field(ge=0, le=254)
    mac_address_bytes: bytes = Field(min_length=6, max_length=6)

    def get_cmd_id(self) -> int:
        return CmdId.ROUTE_ADD

# ==========================================
# Sequence Structures
# ==========================================

class SequenceStep(BaseModel):
    """
    A single step in a batch execution.
    Composition over Inheritance: Contains a specific action.
    """
    target_id: int = Field(ge=0, le=254)
    # For now, we only allow GPIO actions in sequences in MVP
    # In full version this could be Union[SetGpio, SetPwm]
    # But to match binary struct: Cmd(1), Pin(1), Val(1)
    cmd_id: int = Field(default=CmdId.SET_GPIO.value) 
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    delay_ms: int = Field(ge=0, le=4294967295, description="Delay after execution (ms)")

class ExecSequence(DemeterCommand):
    steps: List[SequenceStep] = Field(min_length=1, max_length=30)
    
    def get_cmd_id(self) -> int:
        return CmdId.EXEC_SEQUENCE
