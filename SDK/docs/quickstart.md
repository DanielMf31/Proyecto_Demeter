# Quick Start — Demeter SDK

Get from zero to a complete scientific report in under 10 minutes.

## 1. Installation

```bash
# From the project root
pip install -e "SDK/.[dev]"

# Verify
python -c "from demeter_sdk import DemeterClient; print('OK')"
```

## 2. Create a Client

```python
from demeter_sdk import DemeterClient

# Option A: Pass the key directly
client = DemeterClient(api_key="dk_test_abc123", base_url="http://localhost:8000")

# Option B: Use environment variable (recommended for production)
# export DEMETER_API_KEY="dk_test_abc123"
client = DemeterClient()
```

## 3. Health Check

```python
if not client.ping():
    raise RuntimeError("Demeter server is offline")
print("Server OK")
```

## 4. Fetch and Enrich Data

```python
# Fetch 30 days of telemetry for experiment 1
# Result is cached locally in ~/.demeter_cache/
df = client.get_enriched_data(
    experimento_id=1,
    dias=30,
    fecha_siembra="2025-09-01",   # enables DAP column
    resample_rule="1h",            # optional: smooth to hourly means
)

print(df.columns.tolist())
# ['timestamp', 'temperature', 'humidity', 'node_id',
#  'vpd_kpa', 'dew_point_c', 'wet_bulb_c', 'abs_humidity_g_m3',
#  'enthalpy_kj_kg', 'heat_index_c', 'lsd_kpa',
#  'z_score_temp', 'z_score_hum', 'temp_ma_24h', 'hum_ma_24h',
#  'is_outlier', 'dap_days']

print(df[["timestamp", "vpd_kpa", "dap_days"]].head())
```

## 5. Visualise

```python
# VPD with colour-coded stress zones
fig = client.plot.plot_vpd(df)
fig.savefig("vpd.png", dpi=300, bbox_inches="tight")

# Temperature timeseries with 24h moving average
fig2 = client.plot.plot_timeseries(df, sensor="temperature")
fig2.savefig("temp.png", dpi=300)

# Boxplot — inter-node variability
fig3 = client.plot.plot_boxplot(df, metric="vpd_kpa")
fig3.savefig("vpd_boxplot.png", dpi=300)
```

## 6. Export

```python
# Quick CSV
client.export.to_csv(df, "results/telemetry.csv")

# Full scientific Excel (3 sheets)
client.export.to_excel(
    df_enriched=df,
    path="results/report.xlsx",
    experiment_name="Ensayo Estrés Hídrico V1"
)
```

## 7. One-liner Full Suite

```python
# Everything above in a single call:
out_dir = client.run_full_suite(
    experimento_id=1,
    dias=30,
    output_dir="./demeter_output",
    fecha_siembra="2025-09-01",
)
# Output:
#   demeter_output/Experimento_1/
#   ├── data/enriched_telemetry.csv
#   ├── data/report.xlsx
#   └── plots/{temperature_timeseries,vpd_zones,temperature_boxplot,heatmap}.png
print(f"Results → {out_dir}")
```

## 8. Cache Management

```python
# Second call is instant (reads from ~/.demeter_cache/)
df = client.get_enriched_data(1, dias=30)

# Force fresh download
df = client.get_enriched_data(1, dias=30, force_refresh=True)

# Clear all cached files
n = client.clear_cache()
print(f"Deleted {n} cache files")
```
