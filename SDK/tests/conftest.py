"""
SDK test suite — shared fixtures.
All tests run OFFLINE (no real server required).
"""
from __future__ import annotations
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def make_raw_records(n: int = 48) -> list[dict]:
    """Generate n synthetic telemetry records (hourly, 2 nodes)."""
    base = datetime(2025, 10, 1, 0, 0)
    records = []
    for i in range(n):
        ts = (base + timedelta(hours=i)).isoformat()
        records.append({
            "timestamp": ts,
            "temperature": round(20 + 5 * np.sin(i / 6), 2),
            "humidity":    round(70 + 10 * np.cos(i / 8), 2),
            "node_id":     (i % 2) + 1,
        })
    return records


@pytest.fixture
def raw_records():
    return make_raw_records(48)


@pytest.fixture
def clean_df(raw_records):
    from demeter_sdk import transform
    return transform.pipeline(raw_records)


@pytest.fixture
def enriched_df(clean_df):
    from demeter_sdk import science
    return science.enrich(clean_df, fecha_siembra="2025-09-01")
