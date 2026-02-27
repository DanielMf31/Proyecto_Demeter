RFC: Demeter Python SDK (demeter-sdk)
Proyecto: Demeter (Plataforma IoT de Precisión Agrícola)
Componente: Client-side Python SDK
Estado: Listo para Implementación

## 1. Contexto y Motivación
Actualmente, la plataforma Demeter expone una API REST para consultar las mediciones de los sensores (SHT30, humedad de suelo, etc.) asociados a un experimento. Sin embargo, los investigadores (nuestros usuarios finales) suelen trabajar en entornos como Jupyter Notebooks o Google Colab y necesitan realizar tareas repetitivas de ETL (Extracción, Transformación y Carga) para poder analizar la información.

Necesitamos un SDK oficial en Python que abstraiga la complejidad de la red, maneje la autenticación, limpie los datos crudos del IoT y delegue la computación pesada (generación de gráficas y cálculo de métricas avanzadas) a la máquina del cliente, aliviando la carga de nuestro servidor principal.

## 2. Objetivos y No Objetivos

### Objetivos:
- Proveer una interfaz Pythonic y orientada a objetos (`DemeterClient`).
- Autenticación segura mediante cabeceras HTTP (`X-API-Key`).
- Implementar tolerancia a fallos de red (Retries con exponential backoff).
- Exponer 3 niveles de abstracción de datos: Crudos (Raw), Limpios (Clean) y Enriquecidos (Enriched).
- Incluir un módulo de "Auto-Analytics" (`full_suite`) para exportar reportes y gráficas con una sola línea de código.
- Empaquetable y publicable en PyPI.

### No Objetivos (Fuera de scope para la v1.0):
- El SDK no gestionará conexiones WebSockets en tiempo real (eso es responsabilidad del hardware/Raspberry Pi).
- El SDK no incluirá funciones de administración (crear usuarios o borrar experimentos); es una herramienta de lectura y análisis científico.

## 3. Arquitectura Propuesta
El SDK actuará como un wrapper sobre la librería `requests`, devolviendo estructuras de datos nativas de Data Science (`pandas.DataFrame`).

- **Dependencias estrictas**: `requests`, `pandas`, `matplotlib`, `seaborn`, `urllib3`.
- **Seguridad**: La API Key nunca se guarda en texto plano en el código fuente ni se envía por URL, solo se inyecta en los headers de la sesión.

## 4. Diseño Detallado y API Pública

### 4.1. Core Client (`client.py`)
La clase principal `DemeterClient` manejará la sesión HTTP persistente.
- **Resiliencia**: Configurar un HTTPAdapter con una estrategia Retry(`total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504]`).

### 4.2. Pipeline de Datos (Niveles de Abstracción)
El cliente expondrá tres métodos evolutivos:

1. `get_raw_data(experimento_id, dias)`: Retorna la respuesta JSON literal de la API (`/api/v1/sdk/mediciones`).
2. `get_clean_data(experimento_id, dias)`: 
   - Convierte el raw data a un DataFrame de Pandas.
   - Castea la columna de tiempo a datetime y la establece como índice.
   - Rellena huecos de sensores caídos usando `.interpolate(method='linear')`.
3. `get_enriched_data(experimento_id, dias)`:
   - Llama a `get_clean_data()`.
   - Calcula y añade la columna VPD (Déficit de Presión de Vapor) cruzando las columnas de Temperatura y Humedad.
   - Añade columnas de medias móviles (ej. `temp_media_24h`).

### 4.3. Auto-Analytics Module (`full_suite`)
Método `run_full_suite(experimento_id, output_path)`:
- Crea una estructura de directorios en la máquina local (`/data`, `/plots`).
- Guarda el DataFrame enriquecido como CSV.
- Genera y guarda automáticamente paneles usando Matplotlib/Seaborn (Ej: Panel de Clima, Curva de VPD, Boxplot de varianza de sensores).

## 5. Rendimiento y Optimización
- **Delegación de Cómputo**: Todo el cálculo estadístico y la renderización de gráficas ocurre en la CPU local del investigador, logrando escalabilidad horizontal infinita para la plataforma Demeter.
- **Local Caching (Opcional)**: Los métodos de extracción aceptarán un parámetro `use_cache=True` que guardará un archivo `.parquet`/`.csv` temporal en la máquina del usuario para evitar saturar la API en ejecuciones iterativas de Jupyter Notebooks.

## 6. Estructura del Repositorio a Generar
Se requiere generar los siguientes archivos para publicación:
- `setup.py` (Metadatos para PyPI, versión 0.1.0).
- `demeter_sdk/__init__.py`
- `demeter_sdk/client.py`
- `README.md` (Ejemplo de uso básico y quickstart).
