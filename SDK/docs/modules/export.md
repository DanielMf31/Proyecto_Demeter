# Module Reference — Export

---

## `to_csv(df, path, encoding='utf-8-sig')`

Exports a DataFrame to CSV with UTF-8 BOM encoding (Excel-compatible).

```python
client.export.to_csv(df, "results/telemetry.csv")
```

Creates parent directories automatically. Returns the resolved `Path`.

---

## `to_excel(df_enriched, path, df_raw=None, experiment_name='')`

Creates a structured **3-sheet Excel workbook**:

| Sheet | Contents |
|---|---|
| `Resumen` | Per-column descriptive stats: N, mean, median, std, min, max, P5, P95 |
| `Datos_Enriquecidos` | Full enriched DataFrame with all science columns |
| `Datos_Crudos` | Raw DataFrame (optional, omitted if `df_raw=None`) |

Headers are **bold** with column auto-sizing.

```python
raw = client.get_raw_data(1, dias=30)
df_raw = transform.to_dataframe(raw)
df_enriched = science.enrich(df_raw)

client.export.to_excel(
    df_enriched=df_enriched,
    path="results/ensayo_estres.xlsx",
    df_raw=df_raw,
    experiment_name="Ensayo Estrés Hídrico V2",
)
```

---

## Dependencies

```bash
pip install openpyxl pyarrow   # included in SDK default deps
```
