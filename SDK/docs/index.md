# Demeter SDK v1.0 Documentation

> Python SDK for the **Demeter IoT Agricultural Platform** — from raw sensor readings to publication-quality scientific reports in minutes.

---

## What is Demeter SDK?

The Demeter SDK is a Python library that connects directly to your running Demeter backend and gives researchers, agronomists, and data scientists a clean, high-level API to:

- 📥 **Fetch** telemetry data from experiments and individual plants
- ⚡ **Cache** data locally in Parquet format (skips API if data < 1 hour old)
- 🔬 **Enrich** raw sensor readings with 15 agronomic science formulas
- 📊 **Visualise** data with themed matplotlib/seaborn plots
- 📄 **Export** clean CSV and multi-sheet Excel reports

## Architecture

```
DemeterClient
├── _session.py    → Authenticated HTTPS session (retry + backoff)
├── fetcher.py     → API calls + Parquet cache (TTL = 1h)
├── transform.py   → ETL: type casting, gap filling, resampling
├── science.py     → 15 vectorized agronomic formulas
├── viz.py         → 4 Matplotlib/Seaborn plot functions
└── export.py      → CSV + 3-sheet Excel
```

## Modules

| Module | Reference |
|---|---|
| Core (session, ping, auth) | [core.md](modules/core.md) |
| Fetcher (cache, API) | [fetcher.md](modules/fetcher.md) |
| Transform (ETL) | [transform.md](modules/transform.md) |
| Science (formulas) | [science.md](modules/science.md) |
| Visualisation (plots) | [viz.md](modules/viz.md) |
| Export (CSV / Excel) | [export.md](modules/export.md) |
| Formula Reference | [formulas.md](formulas.md) |

## Quick Start

```bash
pip install -e "SDK/."
```

```python
from demeter_sdk import DemeterClient

client = DemeterClient(api_key="dk_test_xxx")
client.ping()                                    # → True

df = client.get_enriched_data(1, dias=30)
print(df[["timestamp", "vpd_kpa", "dew_point_c", "dap_days"]])

fig = client.plot.plot_vpd(df)
fig.savefig("vpd.png", dpi=300, bbox_inches="tight")

client.export.to_excel(df, "results/report.xlsx")
```

→ Full tutorial: [quickstart.md](quickstart.md)
