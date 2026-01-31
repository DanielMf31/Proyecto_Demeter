# Sistema de Configuración del Proyecto

Este proyecto utiliza un sistema de configuración moderno basado en **Pydantic** y el principio *"Code First"*. La configuración no vive en JSONs estáticos, sino en modelos de Python tipados que sirven como única fuente de verdad.

## 1. Arquitectura de Configuración

La configuración se divide en módulos temáticos (Modelos Pydantic) que se agregan en una clase maestra `Settings`.

```python
class Settings(BaseSettings):
    app_name: str
    llm: LLMConfig
    ocr: OCRConfig
    device: DeviceConfig
    validation: ValidationConfig
    paths: PathsConfig
```

### Ventajas
*   **Validación de Tipos**: Si defines un puerto como entero y pasas un string, falla al instante con un error claro.
*   **Intellisense**: Tu IDE ahora sabe qué opciones existen. Escribe `settings.device.` y verás `port`, `baudrate`, etc.
*   **Variables de Entorno**: Puedes sobrescribir cualquier valor usando `.env`. Ej: `LLM__TEMPERATURE=0.9` (observa el doble guión bajo para anidar).

## 2. Referencia de Parámetros

A continuación se listan todos los módulos configurables y sus valores por defecto.

### Genérico
| Parámetro | Default | Env Var | Descripción |
|-----------|---------|---------|-------------|
| `app_name`| "Ticket Processor AI" | `APP_NAME` | Nombre de la aplicación |
| `debug`   | `False` | `DEBUG` | Activa logs de depuración |
| `log_level`| "INFO" | `LOG_LEVEL` | Nivel de detalle del log |

### LLM (Language Model)
Configuración para el motor de IA. Prefijo Env: `LLM__`

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `enabled` | `True` | Activa/Desactiva llamadas a la IA |
| `provider`| "openai" | Proveedor (openai, anthropic, ollama) |
| `model`   | "deepseek-chat" | Nombre del modelo a usar |
| `temperature` | `0.0` | Creatividad (0=Determinista) |
| `max_tokens` | `4000` | Límite de respuesta |

### OCR (Vision)
Prefijo Env: `OCR__`

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `enabled` | `True` | Activa módulo de visión |
| `provider`| "tesseract" | Motor OCR |
| `language`| "spa" | Idioma esperado |
| `dpi`     | `300` | Calidad de escaneo |

### Validation (Quality Control)
Prefijo Env: `VALIDATION__`

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `confidence_threshold` | `0.75` | Umbral mínimo de confianza para aceptar resultado |
| `strict_mode` | `False` | Si activa, rechaza cualquier fallo menor |
| `allowed_extensions` | `[]` (lista vacía) | Lista de extensiones permitidas para procesar |

### Device (Hardware)
Prefijo Env: `DEVICE__`

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `port`    | *(Requerido)* | Puerto serie (ej: `/dev/ttyUSB0`) |
| `baudrate`| `115200` | Velocidad de conexión |
| `timeout` | `1.0` | Timeout en segundos |

### Paths (Sistema de Archivos)
Define la estructura del proyecto. Se autocalcula relativo a la raíz.

| Parámetro | Default Relativo | Descripción |
|-----------|------------------|-------------|
| **Base** | | |
| `src` | `src` | Código fuente |
| `config` | `config` | Configuración |
| `docs` | `docs` | Documentación |
| **Data Lake** | | |
| `data`    | `data/` | Directorio raíz de datos |
| `input_dir` | `data/input` | Entrada de archivos crudos |
| `output_dir`| `data/output` | Salida de resultados |
| `processed_dir`| `data/processed` | Archivos intermedios/procesados |
| `exports_dir`| `data/exports` | Exportaciones finales |
| `logs_dir`| `data/logs` | Archivos de log rotativos |
| **Componentes** | | |
| `protocols`| `src/.../protocols`| Ruta a definiciones de protocolo |
| `core` | `src/.../core` | Ruta al núcleo de la librería |

## 3. Resolución Automática del Root

El sistema calcula automáticamente dónde está la raíz del proyecto para que no tengas que usar rutas absolutas manuales.

La función `resolve_project_root` busca marcadores de proyecto (como `.git`, `pyproject.toml` o `README.md`) ascendiendo desde la carpeta de configuración. Esto permite que el proyecto funcione idéntico en tu laptop, en Docker o en una Raspberry Pi sin cambiar líneas de código.
