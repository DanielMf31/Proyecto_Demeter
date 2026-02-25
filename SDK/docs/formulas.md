# Scientific Formula Reference

All formulas used by `demeter_sdk.science`. Units and sources documented.

---

## Thermodynamics of Moist Air

### Saturation Vapor Pressure (es)
**Magnus-Tetens formula**

$$e_s = 0.6108 \cdot e^{\frac{17.27 \cdot T}{T + 237.3}}$$

- `T`: Dry-bulb temperature (°C)
- Returns: kPa

### Actual Vapor Pressure (ea)
$$e_a = e_s \cdot \frac{HR}{100}$$

- `HR`: Relative humidity (%)
- Returns: kPa

### Vapor Pressure Deficit (VPD)
$$VPD = \max(0,\ e_s - e_a)$$

- Returns: kPa — **clamped to ≥ 0**

### Dew Point Temperature (Td)
Magnus inversion:
$$T_d = \frac{237.3 \cdot \ln(e_a / 0.6108)}{17.27 - \ln(e_a / 0.6108)}$$

- Returns: °C

### Wet-Bulb Temperature (Stull 2011)
$$T_w = T \cdot \arctan(0.151977 \cdot (HR + 8.313659)^{0.5}) + \arctan(T+HR) - \arctan(HR-1.676331) + 0.00391838 \cdot HR^{1.5} \cdot \arctan(0.023101 \cdot HR) - 4.686035$$

### Absolute Humidity
$$AH = \frac{2165 \cdot e_a}{T + 273.15}$$

- Returns: g/m³

### Mixing Ratio (r)
$$r = \frac{0.622 \cdot e_a}{P - e_a}$$

- `P`: Atmospheric pressure (kPa, default 101.3)
- Returns: kg/kg

### Specific Enthalpy
$$h = 1.006 \cdot T + r \cdot (2501 + 1.86 \cdot T)$$

- Returns: kJ/kg dry air

### Heat Index (Rothfusz, NWS) — valid for T ≥ 27°C
$$HI = -8.785 + 1.611T + 2.339HR - 0.1461TH - 0.01231T^2 - 0.01642H^2 + 0.002212T^2H + 0.000726TH^2 - 0.000004T^2H^2$$

### Leaf Surface Dew (LSD)
Assumes leaf temperature = air − 2°C:
$$LSD = e_s(T_{leaf}) - e_a(T_{air}, HR)$$

- Negative LSD → condensation on leaf surface (fungal risk)

---

## Phenology

### Growing Degree Days (GDD)
$$GDD = \max\left(0,\ \frac{T_{max} + T_{min}}{2} - T_{base}\right)$$

- `T_base` = 10°C for most vegetables
- Returns: °C·day (cumulative sum = development stage)

### Reference Evapotranspiration — Hargreaves-Samani
$$ET_0 = 0.0023 \cdot R_a \cdot (T_{mean} + 17.8) \cdot \sqrt{T_{max} - T_{min}}$$

- `Ra` = extraterrestrial radiation (mm/day, ≈ 15 mm/day for mid-latitude)
- Returns: mm/day

---

## Statistics

### Z-Score
$$z = \frac{x - \mu}{\sigma}$$

### Wallin Risk (1962) — Late Blight
1. Count hours where HR ≥ 90%
2. If count < 10 → Risk = 0 (none)
3. If 10°C ≤ T_mean ≤ 27°C and count ≥ 10 → Risk = 1
4. If count ≥ 20 → Risk = 2

### Days After Planting (DAP)
$$DAP = \lfloor t_{sample} - t_{siembra} \rfloor \text{ (days)}$$
