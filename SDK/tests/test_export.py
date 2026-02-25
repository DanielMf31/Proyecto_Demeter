"""Tests for demeter_sdk.export — CSV and Excel writing."""
from __future__ import annotations
import tempfile
from pathlib import Path

import pandas as pd
import pytest

from demeter_sdk import export


class TestToCsv:
    def test_creates_file(self, enriched_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_csv(enriched_df, Path(tmp) / "out.csv")
            assert path.exists()

    def test_extension_added_if_missing(self, enriched_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_csv(enriched_df, Path(tmp) / "out")
            assert path.suffix == ".csv"

    def test_roundtrip_rows(self, enriched_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_csv(enriched_df, Path(tmp) / "out.csv")
            df2 = pd.read_csv(path, encoding="utf-8-sig")
            assert len(df2) == len(enriched_df)


class TestToExcel:
    def test_creates_xlsx(self, enriched_df, clean_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_excel(
                enriched_df, Path(tmp) / "report.xlsx",
                df_raw=clean_df, experiment_name="Test"
            )
            assert path.exists()
            assert path.suffix == ".xlsx"

    def test_three_sheets_when_raw_provided(self, enriched_df, clean_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_excel(
                enriched_df, Path(tmp) / "r.xlsx", df_raw=clean_df
            )
            xf = pd.ExcelFile(path)
            assert "Resumen" in xf.sheet_names
            assert "Datos_Enriquecidos" in xf.sheet_names
            assert "Datos_Crudos" in xf.sheet_names

    def test_two_sheets_without_raw(self, enriched_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_excel(enriched_df, Path(tmp) / "r.xlsx")
            xf = pd.ExcelFile(path)
            assert "Datos_Crudos" not in xf.sheet_names

    def test_summary_sheet_has_statistics(self, enriched_df):
        with tempfile.TemporaryDirectory() as tmp:
            path = export.to_excel(enriched_df, Path(tmp) / "r.xlsx")
            summary = pd.read_excel(path, sheet_name="Resumen")
            assert "Media" in summary.columns
            assert "Máximo" in summary.columns
            assert len(summary) > 0
