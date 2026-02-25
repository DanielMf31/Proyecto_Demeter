"""
demeter_sdk.fetcher
~~~~~~~~~~~~~~~~~~~
Module 2 — Data Fetching with transparent Parquet cache.

Cache behaviour
---------------
- Files stored at ``{cache_dir}/{resource_type}_{id}_{dias}d.parquet``
- TTL of ``config.cache_ttl_seconds`` (default 1 h). If the file is fresher,
  the API call is skipped entirely.
- ``force_refresh=True`` always re-downloads and overwrites.
"""
from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

import requests

from ._types import SDKConfig, RawMedicion

logger = logging.getLogger("demeter_sdk.fetcher")

# ─── Internal helpers ─────────────────────────────────────────────────────────

def _cache_path(config: SDKConfig, resource: str, resource_id: int, dias: int) -> Path:
    cache_dir = Path(config.cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{resource}_{resource_id}_{dias}d.parquet"


def _is_fresh(path: Path, ttl_seconds: int) -> bool:
    """Return True if the Parquet file exists and was modified within TTL."""
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl_seconds


def _save_parquet(data: list[dict[str, Any]], path: Path) -> None:
    try:
        import pandas as pd
        pd.DataFrame(data).to_parquet(path, index=False, engine="pyarrow")
        logger.debug("Cache written → %s", path)
    except ImportError as exc:
        raise ImportError(
            "pyarrow is required for caching. Install with: pip install pyarrow"
        ) from exc


def _load_parquet(path: Path) -> list[dict[str, Any]]:
    try:
        import pandas as pd
        df = pd.read_parquet(path, engine="pyarrow")
        logger.debug("Cache hit ← %s", path)
        return df.to_dict(orient="records")
    except ImportError as exc:
        raise ImportError(
            "pyarrow is required for caching. Install with: pip install pyarrow"
        ) from exc


def _get_json(
    session: requests.Session,
    url: str,
    params: dict[str, Any],
    timeout: int,
) -> list[dict[str, Any]]:
    resp = session.get(url, params=params, timeout=timeout)
    if resp.status_code == 403:
        raise PermissionError(
            f"HTTP 403 — Invalid API Key or insufficient permissions. URL: {url}"
        )
    if resp.status_code == 404:
        raise LookupError(f"HTTP 404 — Resource not found. URL: {url}")
    resp.raise_for_status()
    return resp.json()


# ─── Public API ───────────────────────────────────────────────────────────────

def fetch_experiment(
    session: requests.Session,
    config: SDKConfig,
    experimento_id: int,
    dias: int = 30,
    force_refresh: bool = False,
) -> list[RawMedicion]:
    """
    Fetch raw telemetry for an experiment, using local Parquet cache.

    Args:
        session:          Authenticated requests.Session (from _session.py).
        config:           SDK configuration (base_url, cache settings…).
        experimento_id:   Experiment ID from the Demeter LIMS.
        dias:             Number of days of history to request (default 30).
        force_refresh:    If True, bypass the cache and re-download.

    Returns:
        List of raw telemetry dicts with keys: timestamp, temperature,
        humidity, node_id.

    Raises:
        PermissionError: If the API key is invalid or lacks access.
        LookupError:     If the experiment ID does not exist.

    Example::

        data = fetch_experiment(session, config, experimento_id=1, dias=30)
    """
    cache = _cache_path(config, "exp", experimento_id, dias)

    if not force_refresh and _is_fresh(cache, config.cache_ttl_seconds):
        logger.info(
            "[CACHE HIT] Exp %d • %dd — skipping API call (age < %ds)",
            experimento_id, dias, config.cache_ttl_seconds,
        )
        return _load_parquet(cache)

    logger.info(
        "[API] Fetching experiment %d • %d days%s",
        experimento_id, dias, " (force_refresh)" if force_refresh else "",
    )
    url = f"{config.base_url}/api/sdk/mediciones/{experimento_id}"
    data = _get_json(session, url, {"dias": dias}, config.timeout)
    logger.info("Retrieved %d records from API.", len(data))

    # Best-effort cache write — never crash main flow
    try:
        _save_parquet(data, cache)
    except Exception as exc:
        logger.warning("Cache write failed (non-fatal): %s", exc)

    return data


def fetch_plant(
    session: requests.Session,
    config: SDKConfig,
    plant_id: int,
    dias: int = 180,
    force_refresh: bool = False,
) -> list[RawMedicion]:
    """
    Fetch raw telemetry for an individual plant from the Redis cache endpoint.

    This endpoint returns data directly from the Redis materialized view
    (``demeter:plant_telemetry:{plant_id}``), so it has near-zero DB load.

    Args:
        plant_id:     Plant LIMS ID.
        dias:         Ignored by the server (returns full 6-month history).
                      Used only for the local cache filename.
        force_refresh: Bypass local Parquet cache.

    Returns:
        List of raw telemetry dicts with keys: timestamp, temperature, humidity.
    """
    cache = _cache_path(config, "plant", plant_id, dias)

    if not force_refresh and _is_fresh(cache, config.cache_ttl_seconds):
        logger.info("[CACHE HIT] Plant %d — skipping API call.", plant_id)
        return _load_parquet(cache)

    logger.info("[API] Fetching plant %d telemetry.", plant_id)
    url = f"{config.base_url}/api/lims/plantas/{plant_id}/telemetry"
    data = _get_json(session, url, {}, config.timeout)
    logger.info("Retrieved %d records for plant %d.", len(data), plant_id)

    try:
        _save_parquet(data, cache)
    except Exception as exc:
        logger.warning("Cache write failed (non-fatal): %s", exc)

    return data


def clear_cache(config: SDKConfig) -> int:
    """
    Delete all cached Parquet files.

    Returns:
        Number of files deleted.
    """
    cache_dir = Path(config.cache_dir).expanduser()
    deleted = 0
    for f in cache_dir.glob("*.parquet"):
        f.unlink()
        deleted += 1
    logger.info("Cache cleared — %d files deleted.", deleted)
    return deleted
