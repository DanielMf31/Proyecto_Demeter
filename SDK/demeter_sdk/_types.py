"""
demeter_sdk._types
~~~~~~~~~~~~~~~~~~
Type definitions and dataclasses for the Demeter SDK.
Following type-first development principles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypedDict, Required, NotRequired


# ─── API Response shapes ──────────────────────────────────────────────────────

class RawMedicion(TypedDict):
    """Raw telemetry record as returned by the Demeter API."""
    timestamp: Required[str]
    temperature: Required[float]
    humidity: Required[float]
    node_id: Required[int]


class PlantMeta(TypedDict):
    """Metadata attached to a plant resource."""
    name: Required[str]
    identificador_fisico: Required[str]
    especie_variedad: Required[str]
    fecha_siembra: Required[str]
    estado_vital: Required[str]
    node_id: Required[int]
    metadata_cientifica: NotRequired[dict[str, Any]]


class ExperimentResponse(TypedDict):
    """Experiment resource as returned by the API."""
    id: Required[int]
    name: Required[str]
    description: NotRequired[str]
    api_key: Required[str]
    created_at: Required[str]
    plants: NotRequired[list[PlantMeta]]


# ─── SDK Configuration ────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SDKConfig:
    """Immutable runtime configuration for DemeterClient."""
    api_key: str
    base_url: str = "http://localhost:8000"
    timeout: int = 30           # seconds per request
    max_retries: int = 3
    backoff_factor: float = 1.0
    cache_dir: str = "~/.demeter_cache"
    cache_ttl_seconds: int = 3600   # 1 hour


# ─── Enriched DataFrame column constants ─────────────────────────────────────

@dataclass(frozen=True)
class Cols:
    """Central registry for DataFrame column names — avoids magic strings."""
    timestamp: str = "timestamp"
    temperature: str = "temperature"
    humidity: str = "humidity"
    node_id: str = "node_id"

    # science.py derived
    vpd_kpa: str = "vpd_kpa"
    dew_point_c: str = "dew_point_c"
    wet_bulb_c: str = "wet_bulb_c"
    abs_humidity_g_m3: str = "abs_humidity_g_m3"
    enthalpy_kj_kg: str = "enthalpy_kj_kg"
    heat_index_c: str = "heat_index_c"
    lsd_kpa: str = "lsd_kpa"
    z_score_temp: str = "z_score_temp"
    z_score_hum: str = "z_score_hum"
    temp_ma_24h: str = "temp_ma_24h"
    hum_ma_24h: str = "hum_ma_24h"
    is_outlier: str = "is_outlier"
    dap_days: str = "dap_days"


COLS = Cols()
