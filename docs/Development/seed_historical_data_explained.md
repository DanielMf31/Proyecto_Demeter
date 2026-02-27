# Análisis Detallado: `seed_historical_data`

> Archivo: `Software/Servidor/Backend/BD/seed_data.py`  
> Función estudiada: `seed_historical_data(db: AsyncSession)` — líneas 63–220

---

## 1. ¿Qué hace esta función en conjunto?

Simula **6 meses de telemetría climática realista** (temperatura + humedad) para 20 plantas
repartidas en 3 experimentos. Los datos se escriben en:

- **PostgreSQL** → tabla `TelemetryTH` (4 320 registros × 20 plantas = **86 400 registros**)
- **Redis** → una clave por planta y otra por experimento (vistas materializadas)

---

## 2. `datetime` y `timedelta` — Los ejes del tiempo

### Importación
```python
from datetime import datetime, timedelta
```

### `datetime.utcnow()`
Devuelve la fecha y hora actuales en **UTC** (Coordinated Universal Time), sin zona horaria.
Se usa como referencia del "ahora":

```python
now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
```

El `.replace(...)` **trunca** el instante actual a la hora en punto (minutos y segundos a cero).
Esto evita que los timestamps generados tengan fracciones de hora y hace que los datos sean
más limpios para el resampling posterior en el SDK.

```
Ejemplo: si ahora son las 14:37:22 UTC → now = 14:00:00 UTC
```

### `timedelta` — diferencias de tiempo
`timedelta` representa una **duración** (no una fecha), y se suma o resta a un `datetime`.

```python
# Retroceder 180 días desde ahora
start_date = now - timedelta(days=180)

# Avanzar hour horas desde start_date
current_time = start_date + timedelta(hours=hour)   # hour ∈ [0, 4319]
```

| Argumento  | Valor         | ¿Qué hace?                              |
|------------|---------------|-----------------------------------------|
| `days=180` | 180           | Retrocede 180 días (6 meses)            |
| `hours=h`  | 0 … 4 319     | Avanza h horas desde el inicio          |
| `days=(i % 7) * 3` | 0, 3, 6, 9, 12, 15, 18 | Escalonado de fechas de siembra |

El rango total de timestamps generado cubre exactamente:
```
[now − 180d,  now − 180d + 1h,  now − 180d + 2h, …,  now − 1h]
```

---

## 3. Ruido gaussiano — la variación aleatoria de sensor

Antes del bucle principal, se generan **todas las perturbaciones aleatorias de golpe**
usando NumPy (operación vectorizada, rápida):

```python
# Forma: (20 plantas, 4320 horas)
t_noises = np.random.normal(0, 0.5, (num_plants, total_hours))  # para temperatura
h_noises = np.random.normal(0, 1.5, (num_plants, total_hours))  # para humedad
```

### ¿Qué es `np.random.normal(µ, σ, shape)`?

Genera números aleatorios siguiendo una **distribución normal (gaussiana)**:

```
    µ = media (centro de la campana)
    σ = desviación estándar (anchura de la campana)
```

| Variable    | µ  | σ   | Efecto sobre la señal                         |
|-------------|-----|------|-----------------------------------------------|
| `t_noises`  | 0   | 0.5  | La temperatura varía ±0.5 °C alrededor de la base |
| `h_noises`  | 0   | 1.5  | La humedad varía ±1.5 % alrededor de la base  |

La media es **0** porque el ruido no debe sesgar la señal: simplemente añade
fluctuaciones pequeñas e independientes, como lo haría un sensor real con sus
imprecisiones intrínsecas o microvariaciones ambientales.

### ¿Por qué generarlo fuera del bucle?

Generarlo una sola vez con shape `(20, 4320)` y luego indexarlo es **órdenes de magnitud
más rápido** que llamar a `np.random.normal` dentro del bucle para cada planta y cada hora.
La indexación `t_noises[p_idx][hour]` accede directamente a la posición ya calculada.

### ¿Por qué cada planta tiene un ruido independiente?

El array tiene dimensión `(num_plants, total_hours)`: cada fila es una planta, cada columna
es una hora. Así, para la misma hora, el nodo 1 y el nodo 7 tienen perturbaciones distintas,
simulando que son sensores físicos separados en ubicaciones ligeramente diferentes del
invernadero.

---

## 4. El ciclo diurno sinusoidal — `diurnal_cycle`

```python
diurnal_cycle = math.cos((current_time.hour - 14) * math.pi / 12)
```

Esta es la parte más física de la función. Simula el **ciclo natural de temperatura y
humedad** a lo largo del día usando una función coseno.

### Desglose término a término

| Término                  | Qué representa                                                             |
|--------------------------|----------------------------------------------------------------------------|
| `current_time.hour`      | Hora del día de la muestra actual (entero 0–23)                            |
| `- 14`                   | Recentra el coseno: el **máximo** se produce a las 14:00 h               |
| `* math.pi / 12`         | Convierte horas a radianes para que el coseno complete **un ciclo en 24 h** |
| `math.cos(...)`          | Retorna un valor entre **−1** y **+1**                                     |

### ¿Por qué 14 horas como pico?

En un invernadero de clima mediterráneo, la temperatura máxima diaria se alcanza tipicamente
entre las 13:00 y las 15:00 (2-3 h después del cénit solar). Se elige 14:00 como valor
representativo.

### ¿Por qué `π / 12`?

El coseno tiene período $2\pi$ radianes. Para que un período completo corresponda a **24 horas**:

$$\text{período} = \frac{2\pi}{\omega} = 24\text{ h} \quad \Rightarrow \quad \omega = \frac{2\pi}{24} = \frac{\pi}{12}$$

### Valores del coseno a lo largo del día

| Hora | `hour − 14` | argumento (rad) | `cos(...)` | Interpretación             |
|------|-------------|-----------------|------------|----------------------------|
| 02:00 | −12        | −π              | **−1.0**   | Mínimo (madrugada fría)   |
| 08:00 | −6         | −π/2            | 0.0        | Temperatura media, subiendo|
| 14:00 | 0          | 0               | **+1.0**   | Máximo (hora pico solar)  |
| 20:00 | +6         | +π/2            | 0.0        | Temperatura media, bajando |
| 02:00 | +12 (=−12) | ±π              | **−1.0**   | Mínimo (nueva madrugada)  |

---

## 5. Temperatura y humedad base — `t_base` y `hr_base`

```python
t_base  = 22.5 + diurnal_cycle * 7.5
hr_base = 62.5 - diurnal_cycle * 22.5
```

Son los valores **deterministas** (sin ruido) para cada hora del día.

### Temperatura base (`t_base`)

```
t_base = 22.5 + diurnal_cycle × 7.5
```

| `diurnal_cycle` | `t_base`         | Hora del día (aprox.) |
|-----------------|------------------|-----------------------|
| +1.0            | 22.5 + 7.5 = **30.0 °C** | 14:00 (pico calor) |
| 0.0             | **22.5 °C**      | 08:00 / 20:00         |
| −1.0            | 22.5 − 7.5 = **15.0 °C** | 02:00 (mínimo) |

- **Temperatura media del día**: 22.5 °C
- **Amplitud diurna**: ±7.5 °C (diferencia entre pico y valle = 15 °C)

### Humedad relativa base (`hr_base`)

```
hr_base = 62.5 - diurnal_cycle × 22.5
```

La humedad es **inversamente proporcional** a la temperatura: cuando hace más calor
el aire seco relativo aumenta su capacidad de absorción y la humedad relativa baja.

| `diurnal_cycle` | `hr_base`        | Hora del día (aprox.) |
|-----------------|------------------|-----------------------|
| +1.0            | 62.5 − 22.5 = **40 %** | 14:00 (más calor, menos humedad) |
| 0.0             | **62.5 %**       | 08:00 / 20:00         |
| −1.0            | 62.5 + 22.5 = **85 %** | 02:00 (más frío, más humedad) |

- **Humedad media del día**: 62.5 %
- **Amplitud diurna**: ±22.5 % (rango total: 40–85 %)

---

## 6. Valores finales con ruido y clipping — `temp_final` y `hr_final`

```python
temp_final = round(max(10.0, min(40.0, t_base + t_noises[p_idx][hour])), 2)
hr_final   = round(max(10.0, min(100.0, hr_base + h_noises[p_idx][hour])), 2)
```

### Construcción capa por capa

```
valor_crudo = base + ruido_gaussiano
              │        └── variación aleatoria pequeña e independiente por planta
              └── valor determinista del ciclo diurno

valor_clipeado = max(límite_inf, min(límite_sup, valor_crudo))

valor_final = round(valor_clipeado, 2)   # 2 decimales
```

### Límites de clipping

| Variable      | Mínimo | Máximo | Justificación                                     |
|---------------|--------|--------|---------------------------------------------------|
| Temperatura   | 10.0 °C | 40.0 °C | Rango seguro de invernadero; fuera → sensor roto |
| Humedad (%)   | 10.0 %  | 100.0 % | Límites físicos de la humedad relativa           |

El clipping evita que el texto del sensor tenga valores **físicamente imposibles**
(temperatura negativa, humedad > 100 %) provocados por la suma aleatoria del ruido en
instantes extremos.

### Ejemplo numérico (planta 3, hora 47 = 23:00 del día 1)

```
hour            = 47          → current_time.hour = 23
diurnal_cycle   = cos((23 − 14) × π / 12) = cos(9π/12) = cos(3π/4) ≈ −0.707

t_base  = 22.5 + (−0.707) × 7.5  ≈ 17.2 °C
hr_base = 62.5 − (−0.707) × 22.5 ≈ 78.4 %

t_noise = t_noises[2][47]  → supón −0.31  (sorteo gaussiano N(0, 0.5))
h_noise = h_noises[2][47]  → supón +1.87  (sorteo gaussiano N(0, 1.5))

temp_final = round(max(10, min(40, 17.2 − 0.31)), 2) = 16.89 °C
hr_final   = round(max(10, min(100, 78.4 + 1.87)), 2) = 80.27 %
```

---

## 7. Flush por lotes y escritura en PostgreSQL

```python
if len(records) >= 10000:
    db.add_all(records)
    await db.commit()
    records = []
```

Los 86 400 objetos `TelemetryTH` **no se crean todos en memoria** antes de insertar.
Cada vez que el buffer `records` alcanza 10 000 elementos, se hace un `commit` parcial y
se vacía la lista. Esto evita picos de RAM que podrían colapsar el proceso dentro de Docker.

---

## 8. Caché Redis — dos claves por tipo de consulta

```python
# Por planta (endpoint de detalle rápido)
cache_key = f"demeter:plant_telemetry:{p.id}"
await redis_manager.redis.set(cache_key, json.dumps(data))

# Por experimento (endpoint de comparativa)
cache_key = f"demeter:raw_data:experimento_{experimentos[idx].id}"
await redis_manager.redis.set(cache_key, json.dumps(exp_cache_data))
```

Redis actúa como **vista materializada**: la API puede servir los 4 320 registros de una
planta sin hacer ni un `SELECT` a PostgreSQL. La clave de experimento agrega los registros
de todas las plantas del mismo en una sola lista JSON.

---

## 9. Resumen visual del pipeline de generación

```
Para cada hora h ∈ [0, 4319]:
│
├─ current_time  = start_date + h horas       (datetime exacto)
│
├─ diurnal_cycle = cos((hour − 14) × π/12)   (−1 a +1, ciclo 24h)
│
├─ t_base        = 22.5 + cycle × 7.5        (15–30 °C)
│  hr_base       = 62.5 − cycle × 22.5       (40–85 %)
│
└─ Para cada planta p ∈ [0, 19]:
   ├─ t_noise = t_noises[p][h]   ~ N(0, 0.5)
   │  h_noise = h_noises[p][h]   ~ N(0, 1.5)
   │
   ├─ temp_final = clip(t_base + t_noise,  10–40)
   │  hr_final   = clip(hr_base + h_noise, 10–100)
   │
   └─ → INSERT TelemetryTH + acumular en dict para Redis
```

El resultado es una señal climática **verosímil**: sigue el ritmo natural del sol,
cada sensor tiene su propia variabilidad aleatoria independiente, y los valores permanecen
dentro de márgenes físicamente válidos.
