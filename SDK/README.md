# Demeter Python SDK (`demeter-sdk`) 🌾

Librería de acceso oficial a la API de **Proyecto Demeter**. Este SDK abstrae las llamadas a red y potencia tu entorno de Data Science devolviendo directamente dataframes de `pandas` limpios y listos para su uso.

## Instalación Local

Estando en la carpeta raíz del SDK (`/SDK`):

```bash
pip install -e .
```

O si utilizas Poetry/UV:
```bash
pip install pandas matplotlib seaborn requests
```

---

## Quickstart

### 1. Inicializar el Cliente

El cliente requiere que proveas la URL de tu API y tu clave secreta de Experimento.

```python
from demeter_sdk import DemeterClient

API_KEY = "DEMETER-EXP-1-SECRET-KEY" # Reemplaza con tu llave
client = DemeterClient(api_key=API_KEY, base_url="http://localhost:8000")
```

### 2. Extracción de Datos Puros

Obtén los datos tal cual están guardados en el Backend.

```python
raw_data = client.get_raw_data(experimento_id=1, dias=7)
print(f"Descargados {len(raw_data)} registros crudos.")
```

### 3. Data Cleansing Integrado (Pandas)

Extrae los datos ya convertidos a DataFrame, con la columna `timestamp` como índice datetime real, y con la imputación lineal automática encargándose de cualquier lectura de sensor vacía.

```python
df_limpio = client.get_clean_data(experimento_id=1, dias=30)
display(df_limpio.head())
```

### 4. Datos Enriquecidos y Cálculo Agronómico

Además del Cleansing, el SDK posee fórmulas científicas integradas offline, liberando de carga al servidor principal. Genera el déficit de presión de vapor (VPD) en kPa y efectúa los cálculos automáticos de medias móviles (24h).

```python
df_cientifico = client.get_enriched_data(experimento_id=1, dias=30)
display(df_cientifico[['timestamp', 'temperature', 'humidity', 'vpd_kpa', 'temp_ma_24h']].head())
```

### 5. Auto-Analytics: "1-Click" Suite 🚀

Para los investigadores, Demeter ofrece un módulo `full_suite` que hace todo de una. Llama a la API, limpia los datos, los enriquece, guarda un dataset local en CSV y renderiza paneles científicos hermosos automáticamente usando Seaborn.

```python
# Crea la magia de una vez
ruta_output = client.run_full_suite(experimento_id=1, dias=30, output_dir="./mis_resultados")
print(f"Reportes y gráficos listos en {ruta_output}")
```
