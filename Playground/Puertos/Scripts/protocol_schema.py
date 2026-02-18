from pydantic import BaseModel, Field
from typing import Literal

# --- Modelos de Protocolo Demeter (Simulados) ---

class GpioCommand(BaseModel):
    """
    Comando enviado por el Cliente (TUI) para actuar sobre el hardware.
    Representa una acción física en el mundo real.
    """
    type: Literal["GPIO_CMD"] = "GPIO_CMD"
    pin: int = Field(..., ge=0, le=40, description="Número de pin físico del ESP32")
    action: Literal["ON", "OFF", "TOGGLE"] = Field(..., description="Acción a realizar")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "GPIO_CMD",
                "pin": 2,
                "action": "TOGGLE"
            }
        }

class ActionResponse(BaseModel):
    """
    Respuesta del Servidor (Backend) confirmando la acción.
    """
    status: Literal["OK", "ERROR"]
    message: str
    pin_state: bool | None = None # True=ON, False=OFF

    class Config:
        json_schema_extra = {
            "example": {
                "status": "OK",
                "message": "GPIO 2 Toggled",
                "pin_state": True
            }
        }
