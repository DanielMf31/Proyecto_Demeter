"""
demeter_sdk.transform
~~~~~~~~~~~~~~~~~~~~~
Module 3 — ETL: type casting, gap filling, and resampling.

These functions accept raw API dicts (or a DataFrame) and output a
clean, analysis-ready DataFrame ready to pass into science.enrich().
"""
from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from ._types import COLS

logger = logging.getLogger("demeter_sdk.transform")


def to_dataframe(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Convert raw API JSON records into a typed Pandas DataFrame.

    - Casts ``timestamp`` to UTC-naive ``datetime64[ns]``.
    - Coerces ``temperature`` and ``humidity`` to ``float64``.
    - Sorts chronologically ascending.

    Args:
        raw_data: List of dicts from ``fetcher.fetch_experiment()`` or
                  ``fetcher.fetch_plant()``.

    Returns:
        Typed DataFrame sorted by timestamp.

    Raises:
        ValueError: If raw_data is empty.
    """
    if not raw_data:
        raise ValueError("raw_data is empty — nothing to convert.")

    df = pd.DataFrame(raw_data)

    # Timestamp: parse ISO-8601 safely, strip timezone to naive UTC
    df[COLS.timestamp] = pd.to_datetime(df[COLS.timestamp], utc=True).dt.tz_localize(None)

    # Numeric coercion (handles strings like "22.5" from some endpoints)
    for col in (COLS.temperature, COLS.humidity):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values(COLS.timestamp).reset_index(drop=True)
    logger.info("to_dataframe(): %d records parsed.", len(df))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning: remove exact duplicate rows and rows with both
    temperature AND humidity missing.

    Args:
        df: DataFrame from ``to_dataframe()``.

    Returns:
        Cleaned DataFrame (new copy).
    """
    n_before = len(df)
    df = df.drop_duplicates().copy()
    # Drop rows where both sensor values are NaN — unrecoverable
    both_nan = df[COLS.temperature].isna() & df[COLS.humidity].isna()
    df = df[~both_nan].reset_index(drop=True)
    logger.info(
        "clean(): removed %d rows (duplicates / full NaN). %d remain.",
        n_before - len(df), len(df),
    )
    return df


def fill_gaps(df: pd.DataFrame, method: str = "linear") -> pd.DataFrame:
    """
    Fill NaN sensor readings using interpolation.

    This handles cases where a sensor momentarily disconnected. Linear
    interpolation is ideal for short gaps (< 30 min). For longer gaps
    use method='time' (requires datetime index).

    Args:
        df:     Clean DataFrame with ``temperature`` and ``humidity`` columns.
        method: Interpolation method passed to ``pd.Series.interpolate()``.
                Options: ``'linear'`` (default), ``'time'``, ``'cubic'``.

    Returns:
        DataFrame with filled gaps (new copy).
    """
    df = df.copy()
    for col in (COLS.temperature, COLS.humidity):
        if col in df.columns:
            n_nan = df[col].isna().sum()
            df[col] = df[col].interpolate(method=method, limit_direction="both")
            if n_nan:
                logger.info("fill_gaps(): interpolated %d NaN in '%s'.", n_nan, col)
    return df


def resample(
    df: pd.DataFrame,
    rule: str = "1h",
    agg: str = "mean",
    node_col: str = COLS.node_id,
) -> pd.DataFrame:
    """
    Resample time-series data to reduce volume and noise.

    Groups by node_id (if present), then resamples to ``rule`` frequency.

    Args:
        df:       DataFrame with a parsed ``timestamp`` column.
        rule:     Pandas offset alias: ``'1h'`` (hourly), ``'1D'`` (daily),
                  ``'30min'``, etc.
        agg:      Aggregation: ``'mean'`` (default), ``'median'``, ``'max'``, …
        node_col: Column to group nodes by (skip grouping if absent).

    Returns:
        Resampled DataFrame with timestamp reset as a regular column.

    Example::

        df_hourly = resample(df, rule='1h')
        df_daily  = resample(df, rule='1D', agg='mean')
    """
    df = df.set_index(COLS.timestamp)

    if node_col in df.columns:
        result = (
            df.groupby(node_col)
            .resample(rule)
            .agg(agg)
            .drop(columns=[node_col], errors="ignore")
            .reset_index()
        )
    else:
        result = getattr(df.resample(rule), agg)().reset_index()

    logger.info("resample('%s'): %d → %d rows.", rule, len(df), len(result))
    return result


def pipeline(
    raw_data: list[dict[str, Any]],
    resample_rule: str | None = None,
    fill_method: str = "linear",
) -> pd.DataFrame:
    """
    Convenience ETL pipeline: to_dataframe → clean → fill_gaps → [resample].

    Args:
        raw_data:      Raw records from the API fetcher.
        resample_rule: Optional Pandas offset alias (e.g. ``'1h'``).
                       If None, no resampling is applied.
        fill_method:   Interpolation method for fill_gaps().

    Returns:
        Clean, ready-to-enrich DataFrame.
    """
    df = to_dataframe(raw_data)
    df = clean(df)
    df = fill_gaps(df, method=fill_method)
    if resample_rule:
        df = resample(df, rule=resample_rule)
    return df
