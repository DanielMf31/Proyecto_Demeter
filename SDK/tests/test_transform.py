"""Tests for demeter_sdk.transform — ETL pipeline."""
from __future__ import annotations
import pandas as pd
import numpy as np
import pytest

from demeter_sdk import transform
from demeter_sdk._types import COLS


class TestToDataframe:
    def test_returns_dataframe(self, raw_records):
        df = transform.to_dataframe(raw_records)
        assert isinstance(df, pd.DataFrame)

    def test_timestamp_is_datetime(self, raw_records):
        df = transform.to_dataframe(raw_records)
        assert pd.api.types.is_datetime64_any_dtype(df[COLS.timestamp])

    def test_timestamp_is_tz_naive(self, raw_records):
        df = transform.to_dataframe(raw_records)
        assert df[COLS.timestamp].dt.tz is None

    def test_sorted_ascending(self, raw_records):
        df = transform.to_dataframe(raw_records)
        assert df[COLS.timestamp].is_monotonic_increasing

    def test_numeric_columns(self, raw_records):
        df = transform.to_dataframe(raw_records)
        assert pd.api.types.is_float_dtype(df[COLS.temperature])
        assert pd.api.types.is_float_dtype(df[COLS.humidity])

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            transform.to_dataframe([])


class TestClean:
    def test_removes_duplicates(self, raw_records):
        doubled = raw_records + raw_records
        df = transform.to_dataframe(doubled)
        cleaned = transform.clean(df)
        assert len(cleaned) == len(raw_records)

    def test_removes_full_nan_rows(self, raw_records):
        df = transform.to_dataframe(raw_records)
        df.loc[0, COLS.temperature] = np.nan
        df.loc[0, COLS.humidity]    = np.nan
        cleaned = transform.clean(df)
        assert len(cleaned) == len(raw_records) - 1


class TestFillGaps:
    def test_no_nans_after_fill(self, raw_records):
        df = transform.to_dataframe(raw_records)
        df.loc[5, COLS.temperature] = np.nan
        df.loc[10, COLS.humidity] = np.nan
        filled = transform.fill_gaps(df)
        assert filled[COLS.temperature].isna().sum() == 0
        assert filled[COLS.humidity].isna().sum() == 0

    def test_original_not_mutated(self, raw_records):
        df = transform.to_dataframe(raw_records)
        df.loc[3, COLS.temperature] = np.nan
        original_nan = df[COLS.temperature].isna().sum()
        transform.fill_gaps(df)
        assert df[COLS.temperature].isna().sum() == original_nan


class TestResample:
    def test_reduces_rows(self, clean_df):
        resampled = transform.resample(clean_df, rule="3h")
        assert len(resampled) < len(clean_df)

    def test_timestamp_still_present(self, clean_df):
        resampled = transform.resample(clean_df, rule="6h")
        assert COLS.timestamp in resampled.columns


class TestPipeline:
    def test_pipeline_returns_dataframe(self, raw_records):
        df = transform.pipeline(raw_records)
        assert isinstance(df, pd.DataFrame)

    def test_pipeline_with_resample(self, raw_records):
        df = transform.pipeline(raw_records, resample_rule="6h")
        assert len(df) < len(raw_records)

    def test_pipeline_no_nans(self, raw_records):
        # Inject NaN before pipeline
        raw_records[3]["temperature"] = None
        df = transform.pipeline(raw_records)
        assert df[COLS.temperature].isna().sum() == 0
