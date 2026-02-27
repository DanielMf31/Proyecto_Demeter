"""
Core/config.py — Enlace con Variables de Entorno del Sistema.

Este archivo actúa como puente, cargando las clases y propiedades de entorno
que vienen provistas en `Software/Common/configuration.py`.
Permite consumir en cualquier lugar: `settings = get_settings()` con Pydantic.
"""

import sys
from pathlib import Path

# Add Software/Common to sys.path
# Backend/Core/config.py -> Backend/Core -> Backend -> Servidor -> Software -> Common
COMMON_PATH = Path(__file__).resolve().parent.parent.parent.parent / "Common"
if str(COMMON_PATH) not in sys.path:
    sys.path.append(str(COMMON_PATH))

from configuration import settings as common_settings

# Proxy or Alias
Settings = common_settings.__class__
settings = common_settings

def get_settings():
    return settings
