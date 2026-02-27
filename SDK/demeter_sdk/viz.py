"""
demeter_sdk.viz
~~~~~~~~~~~~~~~
Module 5 — Scientific Visualisation.

Uses Matplotlib + Seaborn for publication-quality static plots.
All functions return the Matplotlib Figure object so callers can
further customise, show(), or save() it themselves.

VPD zone thresholds (broadly accepted for greenhouse crops):
  < 0.4 kPa  → Risk of fungal disease (blue zone)
  0.4–1.0    → Optimal transpiration (green zone)
  1.0–1.5    → Moderate stress (amber zone)
  > 1.5 kPa  → Severe stress (red zone)
"""
from __future__ import annotations

import logging
from typing import Sequence

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

from ._types import COLS

logger = logging.getLogger("demeter_sdk.viz")

# Consistent style for all plots
_STYLE = "whitegrid"
_PALETTE = "tab10"
_DPI = 150
_FIGSIZE_WIDE = (14, 5)
_FIGSIZE_SQUARE = (10, 6)


def _apply_style() -> None:
    sns.set_theme(style=_STYLE, palette=_PALETTE, font="monospace")


# ─── 1. Time-series ───────────────────────────────────────────────────────────

def plot_timeseries(
    df: pd.DataFrame,
    sensor: str = COLS.temperature,
    title: str | None = None,
    node_ids: Sequence[int] | None = None,
    moving_avg: bool = True,
    figsize: tuple[int, int] = _FIGSIZE_WIDE,
) -> plt.Figure:
    """
    Line plot of a sensor metric over time, coloured by node.

    Args:
        df:          Enriched DataFrame from ``science.enrich()``.
        sensor:      Column to plot (default: ``'temperature'``).
        title:       Plot title (auto-generated if None).
        node_ids:    Subset of node IDs to display (all if None).
        moving_avg:  Overlay the 24h moving average if available.
        figsize:     Figure size (w, h) in inches.

    Returns:
        matplotlib Figure.

    Example::

        fig = plot_timeseries(df, sensor="vpd_kpa")
        fig.savefig("vpd.png", dpi=300, bbox_inches="tight")
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)

    data = df.copy()
    if node_ids and COLS.node_id in data.columns:
        data = data[data[COLS.node_id].isin(node_ids)]

    if COLS.node_id in data.columns:
        for node, group in data.groupby(COLS.node_id):
            ax.plot(group[COLS.timestamp], group[sensor], linewidth=0.9,
                    label=f"Node {node}", alpha=0.8)
            # Overlay moving average
            ma_col = f"{sensor}_ma_24h" if f"{sensor}_ma_24h" in group.columns else None
            if moving_avg and ma_col:
                ax.plot(group[COLS.timestamp], group[ma_col], linewidth=2.0,
                        linestyle="--", alpha=0.95, label=f"Node {node} — MA24h")
    else:
        ax.plot(data[COLS.timestamp], data[sensor], linewidth=0.9)

    ax.set_xlabel("Timestamp", fontsize=11)
    ax.set_ylabel(sensor.replace("_", " ").title(), fontsize=11)
    ax.set_title(title or f"{sensor.upper()} over time", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9, loc="upper right")
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


# ─── 2. VPD Plot with zones ───────────────────────────────────────────────────

def plot_vpd(
    df: pd.DataFrame,
    figsize: tuple[int, int] = _FIGSIZE_WIDE,
    title: str = "Vapor Pressure Deficit (VPD) — Crop Stress Zones",
) -> plt.Figure:
    """
    VPD time-series with coloured stress-zone bands.

    Zone colours:
    - Blue  (< 0.4 kPa) : Risk of fungal disease / condensation
    - Green (0.4–1.0)   : Optimal transpiration
    - Amber (1.0–1.5)   : Moderate stress
    - Red   (> 1.5 kPa) : Severe transpiration stress

    Args:
        df:      Enriched DataFrame with ``vpd_kpa`` column.
        figsize: Figure size tuple.
        title:   Plot title.

    Returns:
        matplotlib Figure.
    """
    if COLS.vpd_kpa not in df.columns:
        raise ValueError(
            "Column 'vpd_kpa' not found. Run science.enrich(df) first."
        )

    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)

    # Draw colour bands FIRST (behind the data)
    zones = [
        (0.0,  0.4,  "#cce5ff", "< 0.4  Fungal Risk"),
        (0.4,  1.0,  "#d4edda", "0.4–1.0  Optimal"),
        (1.0,  1.5,  "#fff3cd", "1.0–1.5  Moderate Stress"),
        (1.5,  3.0,  "#f8d7da", "> 1.5  Severe Stress"),
    ]
    for y0, y1, colour, _ in zones:
        ax.axhspan(y0, y1, alpha=0.35, color=colour, zorder=0)

    # Plot VPD per node
    if COLS.node_id in df.columns:
        for node, group in df.groupby(COLS.node_id):
            ax.plot(group[COLS.timestamp], group[COLS.vpd_kpa],
                    linewidth=0.9, alpha=0.8, label=f"Node {node}")
    else:
        ax.plot(df[COLS.timestamp], df[COLS.vpd_kpa], linewidth=1.0, color="#2a52be")

    # Zone legend patches
    legend_patches = [
        mpatches.Patch(color=c, alpha=0.5, label=lbl)
        for _, _, c, lbl in zones
    ]
    ax.legend(handles=legend_patches, fontsize=9, loc="upper right")

    ax.set_xlabel("Timestamp", fontsize=11)
    ax.set_ylabel("VPD (kPa)", fontsize=11)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylim(bottom=0.0)
    ax.tick_params(axis="x", rotation=25)
    fig.tight_layout()
    return fig


# ─── 3. Boxplot comparison ───────────────────────────────────────────────────

def plot_boxplot(
    df: pd.DataFrame,
    metric: str = COLS.temperature,
    figsize: tuple[int, int] = _FIGSIZE_SQUARE,
    title: str | None = None,
) -> plt.Figure:
    """
    Distribution boxplot per node — ideal for comparing variability
    across multiple plants in one experiment.

    Args:
        df:      DataFrame with ``node_id`` and ``metric`` columns.
        metric:  Column to plot on the Y axis.
        figsize: Figure size.
        title:   Plot title.

    Returns:
        matplotlib Figure.
    """
    _apply_style()
    fig, ax = plt.subplots(figsize=figsize)

    x_col = COLS.node_id if COLS.node_id in df.columns else None
    sns.boxplot(data=df, x=x_col, y=metric, palette=_PALETTE, ax=ax)

    label = metric.replace("_", " ").title()
    ax.set_title(title or f"{label} Distribution by Node", fontsize=13, fontweight="bold")
    ax.set_xlabel("Node ID", fontsize=11)
    ax.set_ylabel(label, fontsize=11)
    fig.tight_layout()
    return fig


# ─── 4. Heatmap (time × node) ────────────────────────────────────────────────

def plot_heatmap(
    df: pd.DataFrame,
    metric: str = COLS.temperature,
    resample_rule: str = "1D",
    figsize: tuple[int, int] = (14, 6),
    title: str | None = None,
) -> plt.Figure:
    """
    2D heat-map of metric intensity across nodes over time.

    Requires ``node_id`` column. Resamples daily by default to prevent
    an overcrowded X-axis.

    Args:
        df:            Enriched DataFrame.
        metric:        Column to visualise.
        resample_rule: Pandas offset alias for time resampling.
        figsize:       Figure size.
        title:         Plot title.

    Returns:
        matplotlib Figure.
    """
    if COLS.node_id not in df.columns:
        raise ValueError("Column 'node_id' required for heatmap.")

    _apply_style()

    pivot = (
        df.set_index(COLS.timestamp)
        .groupby(COLS.node_id)[metric]
        .resample(resample_rule)
        .mean()
        .unstack(level=0)
        .T
    )

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        pivot,
        ax=ax,
        cmap="RdYlGn_r" if "vpd" in metric else "coolwarm",
        linewidths=0.3,
        cbar_kws={"label": metric.replace("_", " ").title()},
    )
    ax.set_title(title or f"{metric.upper()} Heatmap (Node × Time)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Date", fontsize=11)
    ax.set_ylabel("Node ID", fontsize=11)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    return fig
