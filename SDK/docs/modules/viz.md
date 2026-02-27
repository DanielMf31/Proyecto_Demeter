# Module Reference — Viz (Plots)

All plot functions return a `matplotlib.figure.Figure` — you can further
customise, `show()`, or `savefig()` the result.

---

## `plot_timeseries(df, sensor, title, node_ids, moving_avg)`

Line plot coloured by node. Overlays 24h moving average if available.

```python
fig = client.plot.plot_timeseries(df, sensor="vpd_kpa")
fig.savefig("vpd_ts.png", dpi=300, bbox_inches="tight")
```

**Sensors**: `temperature`, `humidity`, `vpd_kpa`, `dew_point_c`, etc.

---

## `plot_vpd(df)`

VPD timeseries with **4 stress-zone colour bands**:

| Band | Range (kPa) | Colour | Meaning |
|---|---|---|---|
| Fungal Risk | < 0.4 | 🔵 Blue | Condensation / botrytis risk |
| Optimal | 0.4 – 1.0 | 🟢 Green | Ideal transpiration |
| Moderate | 1.0 – 1.5 | 🟡 Amber | Stomata partial closure |
| Severe | > 1.5 | 🔴 Red | Wilting, growth stunt |

```python
fig = client.plot.plot_vpd(df)
fig.savefig("vpd.png", dpi=300)
```

---

## `plot_boxplot(df, metric)`

Per-node distribution — ideal for comparing variability across plants.

```python
fig = client.plot.plot_boxplot(df, metric="temperature")
```

---

## `plot_heatmap(df, metric, resample_rule)`

2D heat-map: nodes on Y-axis, dates on X-axis.

```python
fig = client.plot.plot_heatmap(df, metric="vpd_kpa", resample_rule="1D")
fig.savefig("heatmap.png", dpi=300)
```

---

## Saving Plots

```python
# PNG at 300 DPI (publication quality)
fig.savefig("output.png", dpi=300, bbox_inches="tight")

# PDF (vector, for papers)
fig.savefig("output.pdf", bbox_inches="tight")

import matplotlib.pyplot as plt
plt.close(fig)  # Free memory after saving
```
