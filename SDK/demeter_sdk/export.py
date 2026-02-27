"""
demeter_sdk.export
~~~~~~~~~~~~~~~~~~
Module 6 — Scientific Data Export.

Provides clean CSV and structured multi-sheet Excel exports,
following best practices for scientific reproducibility.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger("demeter_sdk.export")


def to_csv(
    df: pd.DataFrame,
    path: str | Path,
    encoding: str = "utf-8-sig",
    index: bool = False,
) -> Path:
    """
    Export a DataFrame to a well-formatted CSV file.

    Uses UTF-8 with BOM (``utf-8-sig``) by default so Excel opens
    it correctly without manual encoding selection.

    Args:
        df:       DataFrame to export (typically the enriched one).
        path:     Output file path. Extension ``.csv`` is added if missing.
        encoding: File encoding (default: ``'utf-8-sig'`` for Excel compat).
        index:    Whether to include the row index (default False).

    Returns:
        Resolved Path of the written file.

    Example::

        export.to_csv(df_enriched, "results/telemetry.csv")
    """
    out = Path(path).expanduser().resolve()
    if out.suffix.lower() != ".csv":
        out = out.with_suffix(".csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out, index=index, encoding=encoding)
    logger.info("CSV saved → %s  (%d rows × %d cols)", out, len(df), len(df.columns))
    return out


def to_excel(
    df_enriched: pd.DataFrame,
    path: str | Path,
    df_raw: pd.DataFrame | None = None,
    experiment_name: str = "Demeter Experiment",
) -> Path:
    """
    Export a structured scientific Excel workbook (.xlsx).

    Sheet layout:
    - **Resumen**            — Descriptive statistics (max, min, mean, std)
                               and summary metrics (VPD mean, outlier count…)
    - **Datos_Enriquecidos** — Full enriched telemetry (all derived columns)
    - **Datos_Crudos**       — Raw temperature + humidity (if ``df_raw`` given)

    Args:
        df_enriched:      Enriched DataFrame from ``science.enrich()``.
        path:             Output file path. Extension ``.xlsx`` is added if missing.
        df_raw:           Optional raw DataFrame for the raw data sheet.
        experiment_name:  Name shown in the Summary header cell.

    Returns:
        Resolved Path of the written workbook.

    Example::

        export.to_excel(df_enriched, "results/report.xlsx",
                        df_raw=df_raw, experiment_name="Ensayo Estrés Salino")
    """
    out = Path(path).expanduser().resolve()
    if out.suffix.lower() != ".xlsx":
        out = out.with_suffix(".xlsx")
    out.parent.mkdir(parents=True, exist_ok=True)

    # Build summary statistics table
    numeric_cols = df_enriched.select_dtypes(include="number").columns.tolist()
    summary_rows = []
    for col in numeric_cols:
        s = df_enriched[col].dropna()
        if len(s) == 0:
            continue
        summary_rows.append({
            "Métrica":    col.replace("_", " ").title(),
            "Columna":    col,
            "N":          len(s),
            "Media":      round(s.mean(), 4),
            "Mediana":    round(s.median(), 4),
            "Desv. Std":  round(s.std(), 4),
            "Mínimo":     round(s.min(), 4),
            "Máximo":     round(s.max(), 4),
            "P5":         round(s.quantile(0.05), 4),
            "P95":        round(s.quantile(0.95), 4),
        })
    df_summary = pd.DataFrame(summary_rows)

    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        # ── Sheet 1: Summary ──
        df_summary.to_excel(writer, sheet_name="Resumen", index=False)
        ws = writer.sheets["Resumen"]
        ws.cell(row=1, column=1).value  # keep existing header
        # Bold top header rows
        from openpyxl.styles import Font, PatternFill
        header_fill = PatternFill("solid", fgColor="2F4F4F")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
        # Auto-width columns
        for col_cells in ws.columns:
            width = max(len(str(c.value or "")) for c in col_cells) + 4
            ws.column_dimensions[col_cells[0].column_letter].width = min(width, 30)

        # ── Sheet 2: Enriched data ──
        df_enriched.to_excel(writer, sheet_name="Datos_Enriquecidos", index=False)
        ws2 = writer.sheets["Datos_Enriquecidos"]
        for cell in ws2[1]:
            cell.font = Font(bold=True)
        for col_cells in ws2.columns:
            width = max(len(str(c.value or "")) for c in col_cells) + 3
            ws2.column_dimensions[col_cells[0].column_letter].width = min(width, 25)

        # ── Sheet 3: Raw data (optional) ──
        if df_raw is not None:
            df_raw.to_excel(writer, sheet_name="Datos_Crudos", index=False)
            ws3 = writer.sheets["Datos_Crudos"]
            for cell in ws3[1]:
                cell.font = Font(bold=True)

    size_kb = out.stat().st_size / 1024
    logger.info(
        "Excel saved → %s  (%.1f KB, %d enriched rows)", out, size_kb, len(df_enriched)
    )
    return out
