# Module Reference — Transform (ETL)

The `transform` module converts raw API dicts into a clean, analysis-ready DataFrame.

---

## Pipeline Functions (use in sequence)

### `to_dataframe(raw_data)` → DataFrame
Converts raw JSON records. Parses ISO timestamps to UTC-naive `datetime64[ns]`, coerces numeric columns.

### `clean(df)` → DataFrame
Removes exact duplicate rows and rows where **both** temperature and humidity are NaN (sensor fully offline).

### `fill_gaps(df, method='linear')` → DataFrame
Interpolates individual NaN readings from momentary sensor dropouts.
Methods: `'linear'` (default), `'time'`, `'cubic'`.

### `resample(df, rule='1h', agg='mean')` → DataFrame
Aggregates per node by time frequency. Reduces noise for plotting.

```python
df_hourly = transform.resample(df, rule='1h')
df_daily  = transform.resample(df, rule='1D', agg='median')
```

---

## `pipeline(raw_data, resample_rule=None, fill_method='linear')`

The recommended entry point — chains all steps:

```python
from demeter_sdk import transform

raw = client.get_raw_data(1, dias=30)
df  = transform.pipeline(raw, resample_rule='1h')
```

Equivalent to:
```python
df = transform.resample(
         transform.fill_gaps(
             transform.clean(
                 transform.to_dataframe(raw))),
         rule='1h')
```

---

## Column Types After `to_dataframe()`

| Column | Type | Notes |
|---|---|---|
| `timestamp` | `datetime64[ns]` | UTC-naive, sorted ascending |
| `temperature` | `float64` | °C |
| `humidity` | `float64` | % Relative Humidity |
| `node_id` | `int64` | Sensor node identifier |
