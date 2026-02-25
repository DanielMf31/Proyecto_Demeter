# Module Reference — Science

All functions operate on **NumPy arrays or Pandas Series** — no Python loops.
Adapted and vectorized from `Backend/Analisis_datos/calculos_agronomicos.py`.

---

## `enrich(df, fecha_siembra=None)` ← Start here

The main convenience function. Adds all derived science columns to a clean DataFrame.

```python
from demeter_sdk import science

df_enriched = science.enrich(df_clean, fecha_siembra="2025-09-01")
```

Columns added: `vpd_kpa`, `dew_point_c`, `wet_bulb_c`, `abs_humidity_g_m3`,
`enthalpy_kj_kg`, `heat_index_c`, `lsd_kpa`, `z_score_temp`, `z_score_hum`,
`temp_ma_24h`, `hum_ma_24h`, `is_outlier`, `dap_days` (if fecha_siembra set).

---

## Thermodynamic Functions

| Function | Returns | Formula |
|---|---|---|
| `saturation_vapor_pressure(T)` | es (kPa) | `0.6108·exp(17.27·T/(T+237.3))` |
| `actual_vapor_pressure(T, HR)` | ea (kPa) | `es · HR/100` |
| `vpd(T, HR)` | VPD (kPa) | `max(0, es − ea)` |
| `dew_point(T, HR)` | Td (°C) | Magnus inversion of ea |
| `wet_bulb(T, HR)` | Tw (°C) | Stull (2011) empirical |
| `absolute_humidity(T, HR)` | AH (g/m³) | `2165·ea / (T+273.15)` |
| `enthalpy(T, HR)` | h (kJ/kg) | `1.006·T + r·(2501 + 1.86·T)` |
| `heat_index(T, HR)` | HI (°C) | Rothfusz (NWS), T ≥ 27°C |
| `leaf_surface_dew(T, HR)` | LSD (kPa) | `es(T−2) − ea(T,HR)` |

### VPD Zones

| Zone | kPa Range | Interpretation |
|---|---|---|
| 🟦 Fungal Risk | < 0.4 | Condensation likely, disease risk |
| 🟩 Optimal | 0.4 – 1.0 | Ideal transpiration |
| 🟨 Moderate Stress | 1.0 – 1.5 | Stomata beginning to close |
| 🟥 Severe Stress | > 1.5 | Wilting risk, growth stunted |

---

## Phenology Functions

| Function | Returns | Use case |
|---|---|---|
| `gdd(T_max, T_min, T_base=10)` | GDD (°C·day) | Predict flowering/fruiting date |
| `chill_hours(T_arr, threshold=7.2)` | integer | Dormancy break prediction |
| `eto_hargreaves(Tmin,Tmax,Tmean,Ra)` | ET₀ (mm/day) | Irrigation scheduling |
| `dap(timestamps, fecha_siembra)` | int Series | Elapsed days since planting |

---

## Statistical Functions

| Function | Returns | Description |
|---|---|---|
| `z_score(arr)` | float array | `(x−μ)/σ` normalisation |
| `detect_outliers(df, col, sigma=3)` | bool Series | Flag `|z| > threshold` |
| `moving_average(df, col, window=24)` | float Series | Rolling mean per node |
| `wallin_risk(HR_arr, T_mean)` | 0/1/2 | Late Blight disease risk level |

---

## Individual Function Usage

```python
import numpy as np
from demeter_sdk import science

T  = np.array([22.5, 23.1, 24.0])
HR = np.array([75.0, 78.0, 82.0])

print(science.vpd(T, HR))           # → [0.562, 0.518, 0.435]
print(science.dew_point(T, HR))     # → [17.9, 18.9, 20.7]
print(science.gdd(30, 18))          # → 14.0 °C·day (base 10°C)
print(science.chill_hours(T))       # → 0 (none below 7.2°C)
```
