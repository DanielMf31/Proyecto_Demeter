"""
demeter_sdk.science
~~~~~~~~~~~~~~~~~~~
Module 4 — Vectorized Agronomic Science Calculations.

All functions operate on NumPy arrays or Pandas Series for maximum
throughput (no Python-level loops). Formulas adapted from:
  Backend/Analisis_datos/calculos_agronomicos.py

Units are explicitly stated in every docstring.
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Union

import numpy as np
import pandas as pd

from ._types import COLS

logger = logging.getLogger("demeter_sdk.science")

# Type alias for array-like inputs
ArrayLike = Union[np.ndarray, pd.Series]


# ─── 1. Thermodynamics of Water and Air ──────────────────────────────────────

def saturation_vapor_pressure(T: ArrayLike) -> np.ndarray:
    """
    Saturation Vapor Pressure using the Magnus-Tetens formula.

    Args:
        T: Dry-bulb temperature in °C (array-like).

    Returns:
        es in kPa.

    Formula:
        es = 0.6108 · exp(17.27·T / (T + 237.3))
    """
    T = np.asarray(T, dtype=float)
    return 0.6108 * np.exp((17.27 * T) / (T + 237.3))


def actual_vapor_pressure(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Actual (ambient) Vapor Pressure.

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        ea in kPa.
    """
    return saturation_vapor_pressure(T) * (np.asarray(HR, dtype=float) / 100.0)


def vpd(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Vapor Pressure Deficit (VPD).

    Critical for plant transpiration management. Values:
    - < 0.4 kPa → Risk of fungal disease
    - 0.4–1.0 kPa → Optimal for most crops
    - 1.0–1.5 kPa → Moderate stress
    - > 1.5 kPa → Severe transpiration stress

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        VPD in kPa, clipped to ≥ 0.
    """
    es = saturation_vapor_pressure(T)
    ea = es * (np.asarray(HR, dtype=float) / 100.0)
    return np.maximum(0.0, es - ea)


def dew_point(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Dew Point Temperature (Magnus inversion).

    If air temperature drops to this value, condensation forms.
    Key indicator for fungal disease risk in greenhouses.

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        Dew point in °C. Returns NaN where HR ≤ 0.
    """
    ea = actual_vapor_pressure(T, HR)
    # Avoid log(0) and negative values
    safe_ea = np.where(ea > 0.0001, ea, np.nan)
    ln_val = np.log(safe_ea / 0.6108)
    return (237.3 * ln_val) / (17.27 - ln_val)


def wet_bulb(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Wet-Bulb Temperature (Stull 2011 empirical formula).

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        Wet-bulb temperature in °C.
    """
    T, HR = np.asarray(T, dtype=float), np.asarray(HR, dtype=float)
    return (
        T * np.arctan(0.151977 * (HR + 8.313659) ** 0.5)
        + np.arctan(T + HR)
        - np.arctan(HR - 1.676331)
        + 0.00391838 * HR ** 1.5 * np.arctan(0.023101 * HR)
        - 4.686035
    )


def absolute_humidity(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Absolute Humidity — mass of water vapor per cubic metre of air.

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        Absolute humidity in g/m³.
    """
    ea = actual_vapor_pressure(T, HR)
    Tk = np.asarray(T, dtype=float) + 273.15
    return (2165.0 * ea) / Tk


def enthalpy(T: ArrayLike, HR: ArrayLike, P_kpa: float = 101.3) -> np.ndarray:
    """
    Specific Enthalpy of moist air (ASHRAE definition).

    Args:
        T:     Dry-bulb temperature (°C).
        HR:    Relative humidity (%).
        P_kpa: Atmospheric pressure in kPa (default: 101.3 kPa = sea level).

    Returns:
        Enthalpy in kJ/kg dry air.
    """
    ea = actual_vapor_pressure(T, HR)
    P_kpa = float(P_kpa)
    r = (0.622 * ea) / (P_kpa - ea)            # mixing ratio kg/kg
    return 1.006 * np.asarray(T, dtype=float) + r * (2501.0 + 1.86 * np.asarray(T, dtype=float))


def heat_index(T: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Heat Index (Rothfusz regression, NWS).

    Only meaningful when T ≥ 27°C. Returns T unchanged for cooler values.

    Args:
        T:  Temperature (°C).
        HR: Relative humidity (%).

    Returns:
        Apparent temperature ("feels like") in °C.
    """
    T, HR = np.asarray(T, dtype=float), np.asarray(HR, dtype=float)
    hi = (
        -8.78469475556
        + 1.61139411 * T
        + 2.338548838 * HR
        - 0.14611605 * T * HR
        - 0.012308094 * T ** 2
        - 0.0164248277 * HR ** 2
        + 0.002211732 * T ** 2 * HR
        + 0.00072546 * T * HR ** 2
        - 0.000003582 * T ** 2 * HR ** 2
    )
    return np.where(T >= 27.0, hi, T)


def leaf_surface_dew(T_air: ArrayLike, HR: ArrayLike) -> np.ndarray:
    """
    Leaf Surface Dew risk index (LSD).

    Assumes leaf temperature ≈ air temperature - 2°C.
    If LSD < 0, condensation on the leaf surface is likely.

    Args:
        T_air: Air temperature (°C).
        HR:    Relative humidity (%).

    Returns:
        LSD in kPa. Negative values indicate condensation risk.
    """
    T_air = np.asarray(T_air, dtype=float)
    T_leaf = T_air - 2.0
    es_leaf = saturation_vapor_pressure(T_leaf)
    ea_air = actual_vapor_pressure(T_air, HR)
    return es_leaf - ea_air


# ─── 2. Phenology & Time ─────────────────────────────────────────────────────

def gdd(T_max: ArrayLike, T_min: ArrayLike, T_base: float = 10.0) -> np.ndarray:
    """
    Growing Degree Days (GDD) — phenological development indicator.

    Args:
        T_max:  Daily maximum temperature (°C).
        T_min:  Daily minimum temperature (°C).
        T_base: Base temperature below which development stops (default 10°C).

    Returns:
        GDD in °C·day, clamped to ≥ 0.

    Formula:
        GDD = max(0, (T_max + T_min) / 2 − T_base)
    """
    return np.maximum(0.0, (np.asarray(T_max, float) + np.asarray(T_min, float)) / 2.0 - T_base)


def chill_hours(T_arr: ArrayLike, threshold: float = 7.2) -> int:
    """
    Chill Hours — count of hourly measurements in (0°C, threshold°C).

    Used to predict dormancy break and bud burst in fruit trees.

    Args:
        T_arr:     Array of hourly temperatures (°C).
        threshold: Upper chill threshold in °C (default 7.2°C).

    Returns:
        Integer count of chill hours.
    """
    T = np.asarray(T_arr, dtype=float)
    return int(np.sum((T > 0.0) & (T < threshold)))


def eto_hargreaves(
    T_min: ArrayLike,
    T_max: ArrayLike,
    T_mean: ArrayLike,
    Ra_mm_day: float = 15.0,
) -> np.ndarray:
    """
    Reference Evapotranspiration — Hargreaves-Samani method.

    Requires only temperature data (no radiation sensors). Ra defaults
    to 15 mm/day, a mid-latitude Mediterranean approximation.

    Args:
        T_min:      Daily minimum temperature (°C).
        T_max:      Daily maximum temperature (°C).
        T_mean:     Daily mean temperature (°C).
        Ra_mm_day:  Extraterrestrial radiation in mm/day equivalent.

    Returns:
        ET₀ in mm/day.

    Formula:
        ET₀ = 0.0023 · Ra · (T_mean + 17.8) · √(T_max − T_min)
    """
    T_min = np.asarray(T_min, float)
    T_max = np.asarray(T_max, float)
    T_mean = np.asarray(T_mean, float)
    return 0.0023 * Ra_mm_day * (T_mean + 17.8) * np.sqrt(np.maximum(0.0, T_max - T_min))


def dap(timestamps: pd.Series, fecha_siembra: Union[str, date, datetime]) -> pd.Series:
    """
    Days After Planting (DAP) — elapsed days since sowing.

    Args:
        timestamps:    Pandas Series of datetime-like timestamps.
        fecha_siembra: Planting date (string 'YYYY-MM-DD', date, or datetime).

    Returns:
        Integer Series of DAP values (0 = planting day).
    """
    if isinstance(fecha_siembra, str):
        t0 = pd.Timestamp(fecha_siembra)
    elif isinstance(fecha_siembra, (date, datetime)):
        t0 = pd.Timestamp(fecha_siembra)
    else:
        raise TypeError(f"fecha_siembra must be str, date or datetime, got {type(fecha_siembra)}")

    ts = pd.to_datetime(timestamps, utc=False)
    return (ts - t0).dt.days.astype(int)


# ─── 3. Statistical & Anomaly ────────────────────────────────────────────────

def z_score(arr: ArrayLike) -> np.ndarray:
    """
    Z-Score normalisation: (x − μ) / σ.

    Args:
        arr: Any numeric array.

    Returns:
        Z-scores. Returns zeros if σ = 0.
    """
    arr = np.asarray(arr, dtype=float)
    mu, sigma = arr.mean(), arr.std(ddof=1)
    return (arr - mu) / sigma if sigma > 0 else np.zeros_like(arr)


def detect_outliers(df: pd.DataFrame, col: str, sigma_threshold: float = 3.0) -> pd.Series:
    """
    Flag outliers using the Z-Score method.

    Samples whose |Z-score| > sigma_threshold are marked True.
    Recommended sigma_threshold = 3.0 for environmental sensors.

    Args:
        df:               DataFrame containing the column.
        col:              Column name to analyse.
        sigma_threshold:  Number of standard deviations before flagging.

    Returns:
        Boolean Series (True = outlier).
    """
    arr = df[col].values
    zs = np.abs(z_score(arr))
    return pd.Series(zs > sigma_threshold, index=df.index, name=COLS.is_outlier)


def moving_average(
    df: pd.DataFrame, col: str, window: int = 24, group_col: str = COLS.node_id
) -> pd.Series:
    """
    Rolling mean per node_id group.

    Args:
        df:        DataFrame with data.
        col:       Column to smooth.
        window:    Rolling window size (samples). 24 ≈ 24h for hourly data.
        group_col: Column to group by (default: «node_id»).

    Returns:
        Series of rolling means aligned to the original index.
    """
    if group_col in df.columns:
        return df.groupby(group_col)[col].transform(
            lambda x: x.rolling(window=window, min_periods=1).mean()
        )
    return df[col].rolling(window=window, min_periods=1).mean()


def wallin_risk(HR_arr: ArrayLike, T_mean: float, hr_threshold: float = 90.0) -> int:
    """
    Wallin (1962) Late Blight Risk Index.

    Counts hours above HR threshold, then assigns a disease risk level.

    Args:
        HR_arr:       Array of hourly relative humidity values (%).
        T_mean:       Mean temperature of the period (°C).
        hr_threshold: HR threshold for counting "risk hours" (default 90%).

    Returns:
        Risk level: 0 = low, 1 = moderate, 2 = high.
    """
    risk_hours = int(np.sum(np.asarray(HR_arr, float) >= hr_threshold))
    if risk_hours < 10:
        return 0
    if 10.0 <= T_mean <= 27.0:
        if risk_hours >= 20:
            return 2
        return 1
    return 0


# ─── 4. Main enrich() convenience ────────────────────────────────────────────

def enrich(df: pd.DataFrame, fecha_siembra: str | None = None) -> pd.DataFrame:
    """
    Enrich a clean telemetry DataFrame with all agronomic science columns.

    Expects columns: ``timestamp``, ``temperature``, ``humidity``.
    Adds:  ``vpd_kpa``, ``dew_point_c``, ``wet_bulb_c``,
           ``abs_humidity_g_m3``, ``enthalpy_kj_kg``, ``heat_index_c``,
           ``lsd_kpa``, ``z_score_temp``, ``z_score_hum``,
           ``temp_ma_24h``, ``hum_ma_24h``, ``is_outlier``
           (and ``dap_days`` if fecha_siembra is provided).

    Args:
        df:             Clean DataFrame from ``transform.clean()``.
        fecha_siembra:  Optional planting date string 'YYYY-MM-DD'.

    Returns:
        New DataFrame with all enrichment columns appended.
    """
    df = df.copy()
    T = df[COLS.temperature].values
    HR = df[COLS.humidity].values

    logger.info("Enriching %d records with agronomic science columns.", len(df))

    df[COLS.vpd_kpa]             = vpd(T, HR)
    df[COLS.dew_point_c]         = dew_point(T, HR)
    df[COLS.wet_bulb_c]          = wet_bulb(T, HR)
    df[COLS.abs_humidity_g_m3]   = absolute_humidity(T, HR)
    df[COLS.enthalpy_kj_kg]      = enthalpy(T, HR)
    df[COLS.heat_index_c]        = heat_index(T, HR)
    df[COLS.lsd_kpa]             = leaf_surface_dew(T, HR)
    df[COLS.z_score_temp]        = z_score(T)
    df[COLS.z_score_hum]         = z_score(HR)
    df[COLS.temp_ma_24h]         = moving_average(df, COLS.temperature)
    df[COLS.hum_ma_24h]          = moving_average(df, COLS.humidity)
    df[COLS.is_outlier]          = detect_outliers(df, COLS.temperature).values

    if fecha_siembra:
        df[COLS.dap_days] = dap(df[COLS.timestamp], fecha_siembra).values

    logger.info("Enrichment complete. Added %d new columns.", len(df.columns))
    return df
