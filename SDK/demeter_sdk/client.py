"""
demeter_sdk.client
~~~~~~~~~~~~~~~~~~
Demeter SDK v1.0 — Main Client Orchestrator.

``DemeterClient`` is the single entry-point for users. It wires together
all internal modules (session, fetcher, transform, science, viz, export)
behind a clean, stable public API.

Example::

    from demeter_sdk import DemeterClient

    client = DemeterClient(api_key="dk_test_xxx", base_url="http://localhost:8000")

    if not client.ping():
        print("Server offline")
    else:
        df = client.get_enriched_data(experimento_id=1, dias=30)
        print(df[["timestamp", "temperature", "vpd_kpa"]].head())
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

from ._types import SDKConfig
from ._session import build_session, ping as _ping
from . import fetcher, transform, science, viz, export

logger = logging.getLogger("demeter_sdk")

# Configure root logger once with a clean handler
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(name)s] %(levelname)s — %(message)s")
    )
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


class DemeterClient:
    """
    Official Demeter IoT Platform SDK Client.

    Provides a high-level interface for:
    - Authenticated API access with auto-retry
    - Local Parquet caching with TTL (default 1 hour)
    - ETL pipeline (type casting, gap filling, resampling)
    - Full agronomic science suite (VPD, GDD, ET₀, dew point…)
    - Publication-quality plots (timeseries, VPD zones, boxplot, heatmap)
    - Scientific export (CSV + multi-sheet Excel)

    Args:
        api_key:    Demeter API key (X-API-Key header). Can also be set via
                    the ``DEMETER_API_KEY`` environment variable.
        base_url:   Base URL of the Demeter backend (default: localhost:8000).
        cache_dir:  Directory for Parquet cache files
                    (default: ``~/.demeter_cache``).
        cache_ttl:  Cache time-to-live in seconds (default: 3600 = 1 hour).
        timeout:    Per-request timeout in seconds (default: 30).
        max_retries: Maximum retry attempts on 5xx errors (default: 3).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "http://localhost:8000",
        cache_dir: str = "~/.demeter_cache",
        cache_ttl: int = 3600,
        timeout: int = 30,
        max_retries: int = 3,
    ) -> None:
        resolved_key = api_key or os.environ.get("DEMETER_API_KEY", "")
        if not resolved_key:
            raise ValueError(
                "api_key is required. Pass it directly or set DEMETER_API_KEY env var."
            )

        self._config = SDKConfig(
            api_key=resolved_key,
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            max_retries=max_retries,
            cache_dir=cache_dir,
            cache_ttl_seconds=cache_ttl,
        )
        self._session = build_session(self._config)
        logger.info("DemeterClient initialised → %s", self._config.base_url)

    # ── M1: Core ─────────────────────────────────────────────────────────────

    def ping(self) -> bool:
        """
        Health-check the Demeter server.

        Returns:
            True if the API is reachable and responding, False otherwise.

        Example::

            client.ping()  # → True
        """
        ok = _ping(self._session, self._config.base_url, timeout=5)
        logger.info("ping() → %s", "OK" if ok else "FAILED")
        return ok

    def clear_cache(self) -> int:
        """Delete all cached Parquet files. Returns count of deleted files."""
        return fetcher.clear_cache(self._config)

    # ── M2+M3: Fetch + ETL ───────────────────────────────────────────────────

    def get_raw_data(
        self,
        experimento_id: int,
        dias: int = 30,
        force_refresh: bool = False,
    ) -> list[dict]:
        """
        Fetch raw telemetry records as a list of dicts (with caching).

        Args:
            experimento_id: Experiment LIMS ID.
            dias:           Days of history (max 180).
            force_refresh:  Bypass Parquet cache.

        Returns:
            List of raw dicts: {timestamp, temperature, humidity, node_id}.
        """
        return fetcher.fetch_experiment(
            self._session, self._config, experimento_id, dias, force_refresh
        )

    def get_plant_data(
        self,
        plant_id: int,
        force_refresh: bool = False,
    ) -> list[dict]:
        """
        Fetch raw telemetry for a single plant (6-month Redis cache endpoint).

        Args:
            plant_id:      Plant LIMS ID.
            force_refresh: Bypass local Parquet cache.

        Returns:
            List of raw dicts.
        """
        return fetcher.fetch_plant(
            self._session, self._config, plant_id, force_refresh=force_refresh
        )

    def get_clean_data(
        self,
        experimento_id: int,
        dias: int = 30,
        resample_rule: str | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Fetch + ETL pipeline: returns a clean, analysis-ready DataFrame.

        Steps performed:
        1. Fetch raw data (with cache)
        2. Parse types, sort chronologically
        3. Remove duplicates
        4. Linear interpolation of sensor gaps
        5. Optional resampling (e.g. ``'1h'``, ``'1D'``)

        Args:
            experimento_id: Experiment ID.
            dias:           Days of history.
            resample_rule:  Optional Pandas offset string (e.g. ``'1h'``).
            force_refresh:  Bypass cache.

        Returns:
            Clean DataFrame with columns: timestamp, temperature, humidity, node_id.
        """
        raw = self.get_raw_data(experimento_id, dias, force_refresh)
        return transform.pipeline(raw, resample_rule=resample_rule)

    def get_enriched_data(
        self,
        experimento_id: int,
        dias: int = 30,
        fecha_siembra: str | None = None,
        resample_rule: str | None = None,
        force_refresh: bool = False,
    ) -> pd.DataFrame:
        """
        Full pipeline: fetch → ETL → agronomic science enrichment.

        Derived columns added (on top of clean data):
        ``vpd_kpa``, ``dew_point_c``, ``wet_bulb_c``,
        ``abs_humidity_g_m3``, ``enthalpy_kj_kg``, ``heat_index_c``,
        ``lsd_kpa``, ``z_score_temp``, ``z_score_hum``,
        ``temp_ma_24h``, ``hum_ma_24h``, ``is_outlier``
        (and ``dap_days`` if ``fecha_siembra`` is provided).

        Args:
            experimento_id:  Experiment ID.
            dias:            Days of history.
            fecha_siembra:   Planting date (``'YYYY-MM-DD'``) for DAP column.
            resample_rule:   Optional Pandas offset string.
            force_refresh:   Bypass cache.

        Returns:
            Fully enriched DataFrame.

        Example::

            df = client.get_enriched_data(1, dias=30, fecha_siembra="2025-09-01")
            print(df[["timestamp", "vpd_kpa", "dap_days"]].head(10))
        """
        df = self.get_clean_data(
            experimento_id, dias, resample_rule=resample_rule, force_refresh=force_refresh
        )
        return science.enrich(df, fecha_siembra=fecha_siembra)

    # ── M5: Visualisation ────────────────────────────────────────────────────

    @property
    def plot(self):
        """Namespace for plot functions. Usage: ``client.plot.vpd(df)``"""
        return viz

    # ── M6: Export ───────────────────────────────────────────────────────────

    @property
    def export(self):
        """Namespace for export functions. Usage: ``client.export.to_csv(df, path)``"""
        return export

    # ── Full Suite ───────────────────────────────────────────────────────────

    def run_full_suite(
        self,
        experimento_id: int,
        dias: int = 30,
        output_dir: str = "./demeter_output",
        fecha_siembra: str | None = None,
        resample_rule: str | None = None,
        force_refresh: bool = False,
    ) -> Path:
        """
        Full extraction → enrichment → export + plots in one call.

        Creates the following structure::

            {output_dir}/Experimento_{id}/
            ├── data/
            │   ├── enriched_telemetry.csv
            │   └── report.xlsx
            └── plots/
                ├── temperature_timeseries.png
                ├── vpd_zones.png
                ├── temperature_boxplot.png
                └── heatmap_temperature.png

        Args:
            experimento_id:  Experiment ID.
            dias:            Days of history.
            output_dir:      Root output directory.
            fecha_siembra:   Planting date for DAP column.
            resample_rule:   Pandas offset string for smoothing.
            force_refresh:   Bypass Parquet cache.

        Returns:
            Path to the experiment output directory.
        """
        exp_dir  = Path(output_dir) / f"Experimento_{experimento_id}"
        data_dir = exp_dir / "data"
        plots_dir = exp_dir / "plots"
        data_dir.mkdir(parents=True, exist_ok=True)
        plots_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=== Full Suite — Exp %d (%d days) ===", experimento_id, dias)

        raw = self.get_raw_data(experimento_id, dias, force_refresh)
        df_raw = transform.pipeline(raw)
        df = science.enrich(df_raw.copy(), fecha_siembra=fecha_siembra)
        if resample_rule:
            df = transform.resample(df, rule=resample_rule)

        # ── Exports ──
        export.to_csv(df, data_dir / "enriched_telemetry.csv")
        export.to_excel(
            df, data_dir / "report.xlsx",
            df_raw=df_raw,
            experiment_name=f"Experimento {experimento_id}",
        )

        # ── Plots ──
        for fname, fig in [
            ("temperature_timeseries.png", viz.plot_timeseries(df, sensor="temperature")),
            ("vpd_zones.png",              viz.plot_vpd(df)),
            ("temperature_boxplot.png",    viz.plot_boxplot(df, metric="temperature")),
            ("heatmap_temperature.png",    viz.plot_heatmap(df, metric="temperature")),
        ]:
            fig.savefig(plots_dir / fname, dpi=300, bbox_inches="tight")
            import matplotlib.pyplot as plt
            plt.close(fig)
            logger.info("Plot saved → %s", plots_dir / fname)

        logger.info("=== Suite complete → %s ===", exp_dir)
        return exp_dir
