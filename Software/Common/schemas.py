from enum import IntEnum
from typing import Annotated, List, Optional, Literal, Union, Dict, Any
from pydantic import BaseModel, Field, ValidationError, field_serializer

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
    TEMP_HUM_REPORT        = 0x0B
    PIN_REPORT             = 0x0C
    SYSTEM_REPORT          = 0x0D
    SENSOR_CLUSTER_REPORT  = 0x0E
    
    # Commands
    SET_GPIO        = 0x10
    SET_PWM         = 0x11
    GET_SENSORS     = 0x20
    EXEC_SEQUENCE   = 0x30

# ==========================================
# Protocol V2 Models (Binary Structure Abstraction)
# ==========================================
class DemeterCommand(BaseModel):
    """
    Base class for all Protocol Commands.

    The `type` field present in subclasses acts as a **discriminator** for JSON
    parsing (Frontend ↔ Backend ↔ Raspberry) and is NEVER serialized to binary
    bytes — pack_frame() only reads the concrete data fields of each subclass.
    """
    target_id: int = Field(ge=0, le=254, description="Node ID of the recipient")
    source_id: Optional[int] = Field(default=None, ge=0, le=255, description="Node ID of the sender")

    def get_cmd_id(self) -> int:
        raise NotImplementedError("Subclasses must implement get_cmd_id")

# --- Control Commands ---
class Ping(DemeterCommand):
    type: Literal["ping"] = "ping"
    def get_cmd_id(self) -> int: return CmdId.PING

class Ack(DemeterCommand):
    type: Literal["ack"] = "ack"
    original_cmd_id: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.ACK

class Nack(DemeterCommand):
    type: Literal["nack"] = "nack"
    original_cmd_id: int = Field(ge=0, le=255)
    error_code: int = Field(ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.NACK

class Syn(DemeterCommand):
    type: Literal["syn"] = "syn"
    context: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SYN

class SynAck(DemeterCommand):
    type: Literal["syn_ack"] = "syn_ack"
    context: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SYN_ACK

class SetGpio(DemeterCommand):
    type: Literal["set_gpio"] = "set_gpio"
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=1)
    flags: int = Field(default=0, ge=0, le=255)
    def get_cmd_id(self) -> int: return CmdId.SET_GPIO

class SetPwm(DemeterCommand):
    type: Literal["set_pwm"] = "set_pwm"
    pin: int = Field(ge=0, le=40)
    value: int = Field(ge=0, le=65535)
    def get_cmd_id(self) -> int: return CmdId.SET_PWM

class GetSensors(DemeterCommand):
    type: Literal["get_sensors"] = "get_sensors"
    def get_cmd_id(self) -> int: return CmdId.GET_SENSORS

class RouteAdd(DemeterCommand):
    type: Literal["route_add"] = "route_add"
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
    type: Literal["exec_sequence"] = "exec_sequence"
    steps: List[SequenceStep] = Field(min_length=1, max_length=30)
    def get_cmd_id(self) -> int: return CmdId.EXEC_SEQUENCE

# --- Reports ---

class TempHumReport(DemeterCommand):
    type: Literal["temp_hum_report"] = "temp_hum_report"
    node_id: int = Field(..., ge=0, le=254)
    temperature: float
    humidity: float
    timestamp: float = 0.0
    def get_cmd_id(self) -> int: return CmdId.TEMP_HUM_REPORT

class SensorClusterEntry(BaseModel):
    plant_id: int = Field(ge=0, le=65535)
    temperature: float
    soil_moisture: float

class SensorClusterReport(DemeterCommand):
    type: Literal["sensor_cluster_report"] = "sensor_cluster_report"
    node_id: int = Field(..., ge=0, le=254)
    entries: List[SensorClusterEntry] = Field(min_length=1, max_length=42)
    def get_cmd_id(self) -> int: return CmdId.SENSOR_CLUSTER_REPORT

class PinReport(DemeterCommand):
    type: Literal["pin_report"] = "pin_report"
    node_id: int = Field(..., ge=0, le=254)
    pin: int = Field(ge=0, le=40)
    state: int = Field(ge=0, le=1)
    def get_cmd_id(self) -> int: return CmdId.PIN_REPORT

class SystemReport(DemeterCommand):
    type: Literal["system_report"] = "system_report"
    node_id: int = Field(..., ge=0, le=254)
    mode: int = Field(ge=0, le=255)
    battery_mv: int = Field(ge=0, le=65535)
    reserved: bytes = Field(default=b'\x00'*5, min_length=5, max_length=5)
    def get_cmd_id(self) -> int: return CmdId.SYSTEM_REPORT


# ==========================================
# Discriminated Union — parseo automático desde JSON
# ==========================================
# Agrupa todos los tipos posibles. Pydantic usa el campo `type` para
# saber cuál instanciar sin ninguna lógica manual.
#
# Uso:
#   from schemas import AnyDemeterCommand
#   cmd = TypeAdapter(AnyDemeterCommand).validate_python(json.loads(raw_json))
#
AnyDemeterCommand = Annotated[
    Union[
        SetGpio,
        SetPwm,
        ExecSequence,
        GetSensors,
        Ping,
        Ack,
        Nack,
        Syn,
        SynAck,
        RouteAdd,
        TempHumReport,
        SensorClusterReport,
        PinReport,
        SystemReport,
    ],
    Field(discriminator="type"),
]
