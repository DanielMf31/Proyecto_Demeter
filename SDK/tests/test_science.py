"""Tests for demeter_sdk.science — all formula functions."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from demeter_sdk import science
from demeter_sdk._types import COLS


class TestThermodynamics:
    def test_saturation_vp_known_value(self):
        # At 20°C es ≈ 2.338 kPa (Tetens)
        es = science.saturation_vapor_pressure(np.array([20.0]))
        assert abs(es.item() - 2.338) < 0.01

    def test_vpd_clipped_to_zero(self):
        # VPD must never be negative
        result = science.vpd(np.array([15.0]), np.array([100.0]))
        assert result.item() == 0.0

    def test_vpd_increases_with_temperature(self):
        vpd_low  = science.vpd(np.array([20.0]), np.array([60.0]))
        vpd_high = science.vpd(np.array([35.0]), np.array([60.0]))
        assert vpd_high.item() > vpd_low.item()

    def test_vpd_decreases_with_humidity(self):
        vpd_dry  = science.vpd(np.array([25.0]), np.array([40.0]))
        vpd_wet  = science.vpd(np.array([25.0]), np.array([80.0]))
        assert vpd_dry.item() > vpd_wet.item()

    def test_dew_point_below_temperature(self):
        td = science.dew_point(np.array([25.0]), np.array([60.0]))
        assert td.item() < 25.0

    def test_dew_point_equals_temp_at_100pct(self):
        td = science.dew_point(np.array([20.0]), np.array([100.0]))
        assert abs(td.item() - 20.0) < 0.2

    def test_absolute_humidity_positive(self):
        ah = science.absolute_humidity(np.array([22.0]), np.array([70.0]))
        assert ah.item() > 0

    def test_enthalpy_increases_with_humidity(self):
        h_dry = science.enthalpy(np.array([25.0]), np.array([30.0]))
        h_wet = science.enthalpy(np.array([25.0]), np.array([90.0]))
        assert h_wet.item() > h_dry.item()

    def test_heat_index_unchanged_below_27(self):
        hi = science.heat_index(np.array([20.0]), np.array([80.0]))
        assert hi.item() == 20.0  # Returns T unchanged when T < 27°C

    def test_leaf_surface_dew_negative_at_high_humidity(self):
        lsd = science.leaf_surface_dew(np.array([15.0]), np.array([99.0]))
        assert lsd.item() < 0  # condensation expected


class TestPhenology:
    def test_gdd_base_10(self):
        assert science.gdd(30, 18) == pytest.approx(14.0)

    def test_gdd_clamped_to_zero(self):
        assert science.gdd(8, 5, T_base=10.0) == 0.0

    def test_chill_hours_count(self):
        # T in (0, 7.2): 5.0 ✓, 6.0 ✓, 0.5 ✓  |  8.0 > 7.2 ✗, 20 ✗, -1 ✗
        T = np.array([5.0, 6.0, 8.0, 20.0, 0.5, -1.0])
        assert science.chill_hours(T, threshold=7.2) == 3  # 5.0, 6.0, 0.5

    def test_eto_hargreaves_positive(self):
        et0 = science.eto_hargreaves(T_min=15, T_max=30, T_mean=22.5)
        assert float(et0) > 0

    def test_dap_increases_monotonically(self):
        ts = pd.Series(pd.date_range("2025-10-01", periods=10, freq="D"))
        dap = science.dap(ts, "2025-09-01")
        assert list(dap) == list(range(30, 40))


class TestStatistics:
    def test_zscore_mean_near_zero(self):
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = science.z_score(arr)
        assert abs(result.mean()) < 1e-10

    def test_zscore_std_near_one(self):
        arr = np.linspace(0, 100, 50)
        result = science.z_score(arr)
        assert abs(result.std(ddof=1) - 1.0) < 1e-10

    def test_detect_outliers_known(self):
        # Build array where the last value is a clear outlier
        base = np.array([20.0] * 100)
        base[-1] = 200.0
        df = pd.DataFrame({"temperature": base})
        outliers = science.detect_outliers(df, "temperature", sigma_threshold=3.0)
        assert outliers.iloc[-1] is True or outliers.iloc[-1] == True

    def test_moving_average_length(self):
        df = pd.DataFrame({
            COLS.temperature: np.random.uniform(18, 30, 100),
            COLS.node_id: [1] * 100,
        })
        ma = science.moving_average(df, COLS.temperature, window=24)
        assert len(ma) == 100

    def test_wallin_risk_levels(self):
        high_hr = np.array([95.0] * 25)
        assert science.wallin_risk(high_hr, T_mean=18.0) == 2

        low_hr = np.array([70.0] * 25)
        assert science.wallin_risk(low_hr, T_mean=18.0) == 0


class TestEnrich:
    def test_enrich_adds_all_columns(self, enriched_df):
        expected = [
            COLS.vpd_kpa, COLS.dew_point_c, COLS.wet_bulb_c,
            COLS.abs_humidity_g_m3, COLS.enthalpy_kj_kg, COLS.heat_index_c,
            COLS.lsd_kpa, COLS.z_score_temp, COLS.z_score_hum,
            COLS.temp_ma_24h, COLS.hum_ma_24h, COLS.is_outlier, COLS.dap_days,
        ]
        for col in expected:
            assert col in enriched_df.columns, f"Missing column: {col}"

    def test_enrich_no_nans_in_vpd(self, enriched_df):
        assert enriched_df[COLS.vpd_kpa].isna().sum() == 0

    def test_enrich_dap_positive(self, enriched_df):
        assert (enriched_df[COLS.dap_days] >= 0).all()
