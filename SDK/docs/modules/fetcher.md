# Module Reference — Fetcher (Cache)

The `fetcher` module handles all API communication and transparent local caching.

---

## Cache Behaviour

Files are stored at: `~/.demeter_cache/{resource}_{id}_{dias}d.parquet`

```
~/.demeter_cache/
├── exp_1_30d.parquet     ← Experiment 1, 30 days
├── exp_1_180d.parquet    ← Experiment 1, 180 days
└── plant_5_180d.parquet  ← Plant 5 telemetry
```

**TTL = 1 hour** (configurable via `cache_ttl` in `DemeterClient`).
If the file is fresher than the TTL, the API call is skipped entirely.

---

## `fetch_experiment(session, config, experimento_id, dias, force_refresh)`

Fetch raw telemetry for an experiment.

```python
from demeter_sdk import fetcher
data = fetcher.fetch_experiment(session, config, experimento_id=1, dias=30)
```

## `fetch_plant(session, config, plant_id, dias, force_refresh)`

Fetch 6-month telemetry for a single plant from Redis.

```python
data = fetcher.fetch_plant(session, config, plant_id=5)
```

## `clear_cache(config)` → int

Delete all `.parquet` files. Returns count deleted.

```python
n = client.clear_cache()
print(f"Deleted {n} files")
```

---

## Via DemeterClient

```python
# Standard (uses cache if fresh)
raw = client.get_raw_data(1, dias=30)

# Force API re-download
raw = client.get_raw_data(1, dias=30, force_refresh=True)

# Per-plant data
raw = client.get_plant_data(plant_id=3)
```

---

## Errors

| Exception | When |
|---|---|
| `PermissionError` | HTTP 403 — invalid API key |
| `LookupError` | HTTP 404 — experiment/plant not found |
| `requests.exceptions.ConnectionError` | Server unreachable |
